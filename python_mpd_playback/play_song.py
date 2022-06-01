from mpd import MPDClient
client = MPDClient() 
client.timeout = 10
client.idletimeout = None
client.connect("localhost", 6600)
print client.mpd_version

# print client.search('title', 'todd terje')


# client.playlistclear('Band')
client.load('Fedt')

print client.playlist()

client.play(0)
client.stop()
print 'test'
