from .models import PrivateChat

def create_chat(user1, user2):
	try:
		chat = PrivateChat.objects.get(user1=user1, user2=user2)
	except PrivateChat.DoesNotExist:
		try:
			chat = PrivateChat.objects.get(user1=user2, user2=user1)
		except PrivateChat.DoesNotExist:
			chat = PrivateChat(user1=user1, user2=user2)
			chat.save()
	return chat