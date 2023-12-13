# from models import User
# from test.utils import reset_db

# def test_create_account_page(test_client):
#     response = test_client.get('/')
#     data = response.data.decode('utf-8')
#     assert response.status_code == 200

# def test_player_profile(test_client):
#     response = test_client.post('/profile', data={
#         'profile': 'username'
#     }, follow_redirects=True)
#     assert response.status_code == 200

#     data = response.decode('utf-8')

# def test_create_post(test_client):
#     response = test_client.post('/create_post')