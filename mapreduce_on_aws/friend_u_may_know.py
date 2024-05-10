from pyspark import SparkContext, SparkConf
from itertools import combinations

conf = SparkConf().setMaster("local[*]").setAppName("FriendYouMayKnow")
sc = SparkContext(conf=conf)

'''
Map each line to get all the combinations of 2 friends
who have the user figuring on the same line as common friend.

Input:<User><TAB><Friends>
Output:((<Friend1>,<Friend2>), 1)

For the users who have no friends, we emit
((<User>,None), 0)

'''
def mutual_friends_mapper(line):
    usr_friends = line.split("\t")
    user = usr_friends[0]
    friends = usr_friends[1].split(",")
    if '' in friends:
        yield ((int(user), None), 0)
    else:
        int_friends = list(map(int, friends))
        int_friends.sort()
        have_mutual_friends = list(combinations(int_friends, 2))
        mutual_fr_mapping = map(lambda m: ((int(m[0]),int(m[1])), 1), have_mutual_friends)
        for mf in mutual_fr_mapping:
            yield mf

'''
Map each line to get all the direct friends
related to the user figuring on the same line.

Input:<User><TAB><Friends>
Output:((<User>,<Friend>), -1)

'''
def close_friends_mapper(line):
    usr_friends = line.split("\t")
    user = usr_friends[0]
    friends = usr_friends[1].split(",")
    if not '' in friends:
        close_fr_mapping = map(lambda f: (tuple(sorted((int(user),int(f)))), -1), friends)
        for cf in close_fr_mapping:
            yield cf


# Create a RDD from the file
rddFromFile = sc.textFile("soc-LiveJournal1Adj.txt")

# Apply the mutual_friends_mapper against the RDD
rdd1 = rddFromFile.flatMap(lambda l: mutual_friends_mapper(l))
# Apply the close_friends_mapper against the RDD
rdd2 = rddFromFile.flatMap(lambda l: close_friends_mapper(l))

# Merge the 2 resulting RDD
rdd3 = sc.union([rdd1, rdd2])

'''
Reduce the set of Key-Value pairs by summing the
values for each encountered key.

An exception was made for the direct friends and those
who have no friends. We keep the values at -1 and 0
respectively.

Input:((<User1>,<User2>), X) where X = 1, -1 or 0
Output:((<User1>,<User2>), X) where X = Number of the mutual friends, -1 or 0

'''
rdd4=rdd3.reduceByKey(lambda x,y: x + y if x > 0 and y > 0 else ( 0 if x == 0 or y == 0 else -1))


'''
Get rid of the Key-Value pairs having -1 as a value.

For the remaining keys, we map each key to get 2 new keys.
An exception was made for the Key-Value pairs having 0 as
value. We keep the key as it is.

Input:((<User1>,<User2>), X) where X = Number of the mutual friends
    ((<User>,None), 0)
Output:((<User1>,<User2>), X), ((<User2>,<User1>), X), ((<User>,None), 0)

'''
rdd5 = rdd4.filter(lambda r: r[1] >= 0) \
    .flatMap(lambda r: [(r[0][0], (r[0][1], r[1])), (r[0][1], (r[0][0], r[1]))] if r[1] > 0 else [(r[0][0], (None, 0))])


'''
Group by key and map the resulting list of values to
be sorted first by the number of mutual friends in descending 
order and then by the User ID in ascending order.

We take the first 10 values of the list of recommendations
and sort the keys by User ID in ascending order.

Input:((<User1>,<User2>), X), ((<User2>,<User1>), X), ((<User>,None), 0)
Output:(User, [(Recommendation1, X1), (Recommendation2, X2), ...]) where the Xn are the number of mutual friends

'''
rdd6 = rdd5.groupByKey() \
    .mapValues(lambda x: sorted(list(x), key=lambda y: (-y[1], y[0]))[:10]) \
    .sortBy(lambda x: x[0])

# Format the results as such <User><TAB><Recommendations>
rdd7 = rdd6.map(lambda row: f"{row[0]}\t{row[1]}" if row[1][0][0] != None else f"{row[0]}\t[]")

# Output the results to a file
rdd7.coalesce(1).saveAsTextFile('recommendations')
