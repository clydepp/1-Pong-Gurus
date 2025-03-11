import boto3

def create_achievements_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.create_table(
        TableName='Achievements',
        KeySchema=[
            {
                'AttributeName': 'username',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'achievement',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'username',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'achievement',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={import boto3

# Call to add achievements
def add_achievement(dynamodb=None): # this should add an achievement to the table - and print on the screen that it was added
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    
# users table has username: total_score, most_hits // these will be constantly updated after each game
def create_users_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.create_table(
        TableName='Users',
        KeySchema=[
            {
                'AttributeName': 'username',
                'KeyType': 'HASH'  # Partition key 'Primary'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'username',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    return table

def create_preload_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.create_table(
        TableName='AchievementsPre',
        KeySchema=[
            {
                'AttributeName': 'achievementID',
                'KeyType': 'HASH'  # Partition key 'Primary'
            },

        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'achievementID',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    return table

def create_achievement_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.create_table(
        TableName='Achievements',
        KeySchema=[
            {
                'AttributeName': 'achievementID',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'username',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'achievementID',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'username',
                'AttributeType': 'S'    
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    return table

# initialise user in users table (sends the data after the first round)
def initialize_user(dynamodb=None, username="", game_score=0, game_hits=0):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table('Users')
    response = table.put_item(
        Item={
            'username': username, 
            'info': {
                'total_score': game_score,
                'max_hits': game_hits
            }
        }
    )
    return response

# called at the end of each round
def update_user_scores(dynamodb=None, username="", game_score=0, game_hits=0):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table('Users')
    
    # Update total_score and max_hits conditionally
    response = table.update_item(
        Key={
            'username': username
        },
        UpdateExpression="SET info.total_score = info.total_score + :val, info.max_hits = :hits",
        ConditionExpression="attribute_not_exists(info.max_hits) OR info.max_hits < :hits",
        ExpressionAttributeValues={
            ':val': game_score,
            ':hits': game_hits
        },
        ReturnValues="UPDATED_NEW"
    )
    return response

# adds achievement from preloaded table and takes username
def add_achievement(dynamodb=None, achievementID="", username=""):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    
    table = dynamodb.Table('Achievements')
    response = table.put_item (
        Item={
            'achievementID': achievementID,
            'username': username
        },
    )
    print(username , 'unlocked a new achievement:' , achievementID)
    return response
    
def preload_achievements(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    load_table = create_preload_table(dynamodb)

    achievements = [
        {
            'achievement_id': '10HITS',
            'name': '10 Hits',
            'description': 'Get 10 hits in a single game',
            'requirement_type': 'hits_in_game',
            'threshold': 10,
        },
        {
            'achievement_id': '25HITS',
            'name': '25 Hits',
            'description': 'Get 25 hits in a single game',
            'requirement_type': 'hits_in_game',
            'threshold': 25,
        },
        {
            'achievement_id': '50HITS',
            'name': '50 Hits',
            'description': 'Get 50 hits in a single game',
            'requirement_type': 'hits_in_game',
            'threshold': 50,
        },
        {
            'achievement_id': '20TOTAL',
            'name': 'Score 20',
            'description': 'Reach a total score of 20 points',
            'requirement_type': 'total_score',
            'threshold': 20,
        },
        {
            'achievement_id': '50TOTAL',
            'name': 'Score 50',
            'description': 'Reach a total score of 50 points',
            'requirement_type': 'total_score',
            'threshold': 50,
        },
        {
            'achievement_id': '100TOTAL',
            'name': 'Score 100',
            'description': 'Reach a score of 100 points',
            'requirement_type': 'total_score',
            'threshold': 100,
        },
        {
            'achievement_id': 'FIRST_GAME',
            'name': 'First Game',
            'description': 'Complete your first game',
            'requirement_type': 'games_played',
            'threshold': 1,
        }
    ]
    
if __name__ == '__main__':
    users_table = create_users_table()
    achievement_ref_table = preload_achievements()
    achievements_table = create_achievement_table()
    print("Table status:", users_table.table_status)

            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    return table

if __name__ == '__main__':
    achievements_table = create_achievements_table()
    print("Table status:", achievements_table.table_status)
