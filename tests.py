import gdata.gauth
import gdata.apps.groups.client

DOMAIN = ''
EMAIL = ''
PASSWORD = ''

groupClient = gdata.apps.groups.client.GroupsProvisioningClient(domain=DOMAIN)
groupClient.ClientLogin(email=EMAIL, password=PASSWORD, source='apps')

groupClient.RetrieveAllGroups()
