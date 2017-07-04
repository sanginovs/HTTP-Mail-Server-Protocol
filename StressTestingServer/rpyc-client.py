import rpyc

# Grab a connection to the server
client = rpyc.connect("104.198.105.38", 8888)

# The "root" is the class we registered with the server.
# So, all exposed methods can be called off of the "root".

# Now, lets test the quote server.
# My client loops through four different users. 
# Why? because I wanted to test more than a single username.
usernames = ["jadudm", "vaderd", "potterh", "belaqual"]

# Loop through each of the usernames.
for u in usernames:
  # First, make sure the user is registered.
  client.root.register(u)
  # Print a message when I'm done.
  print("Registered {0}".format(u))
  # Add a quote, so we see if it shows up.
  client.root.add_quote(u, "This is an added quote from {0}.".format(u))

  # Now, I'm going to request (and print out) five quotes.
  # Why I declared a variable *right here* I don't know. It makes 
  # little sense...
  numquotes = 5
  # Loop, requesting five quotes.
  for i in range(0, numquotes):
    # Invoke the "get_quote" method on the server and print
    # the string that it returns.
    print(client.root.get_quote(u))
  
  # When I'm done looping, find out how many quotes this user
  # has requested. If the server just started, it should
  # be that I requested five quotes.
  requested = client.root.quotes_requested(u) 
  print("Quotes found: {0}".format(requested))
  print("Done testing user '{0}'.".format(u))
  
