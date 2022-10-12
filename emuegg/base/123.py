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
    url = ''
    for cor in cors:
        url = cor[2]
        print(url)
    url1 = [39.906217, 116.3912757, 'https://en.wikipedia.org/wiki/Beijing'][2]
    print(url1)
if __name__ == '__main__':
    view()