import os
from unittest.mock import patch, MagicMock
os.environ['QUEUE_URL'] = 'test_url'
from mafiaUpdateGame import lambda_handler

def test_ValidRequest_Returns200():
    teamId = 'test'
    userId = 'testUser'
    with patch('mafiaUpdateGame.GameStateRepo') as mockRepo:
        with patch('mafiaUpdateGame.GameStateManager') as mockStateManager:
            with patch('mafiaUpdateGame.json.dumps'):
                with patch('mafiaUpdateGame.boto3'):
                    result = lambda_handler({"body": f"team_id={teamId}&user_id={userId}", "action" : "ADD_PLAYER", "isBase64Encoded": False},None)
    
    assert result['statusCode'] == 200

def test_SuccessfulRequestWithOptionalArgs_SendsDataToManageSlackQueue():
    teamId = 'test'
    userId = 'testUser'
    action = 'ADD_PLAYER'
    with patch('mafiaUpdateGame.GameStateRepo') as mockRepo:
        mockState = mockRepo.return_value._serializeGame.return_value
        with patch('mafiaUpdateGame.GameStateManager') as mockStateManager:
            transition_result = mockStateManager.return_value.transition.return_value = True
            with patch('mafiaUpdateGame.json.dumps') as mockJsonDumper:
                with patch('mafiaUpdateGame.boto3') as mockboto3:
                    mockAwsClient = mockboto3.client.return_value
                    with patch('mafiaUpdateGame.extract_user_id') as idExtractor:
                        result = lambda_handler({"body": f"team_id={teamId}&user_id={userId}&text=testTest", "action" : action, "isBase64Encoded": False},None)
                        mockAwsClient.send_message.assert_called_with(QueueUrl = 'test_url', MessageBody=mockJsonDumper.return_value)
                        mockJsonDumper.assert_any_call({'state':mockState, 'action':action, 'source':userId, 'target' : idExtractor.return_value})
                        #messageBuilder.assert_called_with(mockState, transition_result, action, userId, idExtractor.return_value)

    
    assert result['statusCode'] == 200
