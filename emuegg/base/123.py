import geocoder

def view():
    capitals = ['Beijing', 'Canberra', 'Tokyo', 'Seoul', 'Manila', 'Hanoi', 'Kuala_Lumpur', 'Jakarta', 'New_Delhi', 'Bangkok']
    cors = []
    for capital in capitals:
        Capitallocation = geocoder.osm(capital)
        capLat = Capitallocation.lat
        capLng = Capitallocation.lng
        url1 = "https://en.wikipedia.org/wiki/" + capital
        cors.append([capLat, capLng, url1])
    
    
    print(cors)

if __name__ == '__main__':
    view()