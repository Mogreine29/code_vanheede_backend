import matplotlib.pyplot as plt
import folium

def plotMap(trucks, DicoBulles, depot, outf):
    #df = cws.all_coords
    
    color_index = 0
    locations = []
    long = []
    lat = []
    
    legend_html = """<div style="position:fixed; bottom:10px; left:10px; border:2px solid black; z-index:9999; font-size:14px;">&nbsp;<b>test:</b><br>"""

    
    x, y = "Latitude", "Longitude"
    color = "Cost"
    size = "Staff"
    popup = "Street Address"
    
    ## create color column
    lst_colors=["red","green","orange", "blue", "black", "pink", "yellow", "brown", "purple", "grey" ]
    
    ## initialize the map with the starting location
    map_ = folium.Map(location=[depot.latitude, depot.longitude], tiles="cartodbpositron",
                      zoom_start=10)
    
    
    folium.Marker(
    location=[ 50.7250, 3.3211],
    popup="Dottignies",
    icon=folium.Icon(color="green"),
    ).add_to(map_)
    
    folium.Marker(
    location=[ 50.3690,  3.9670],
    popup="Quevy",
    icon=folium.Icon(color="blue"),
    ).add_to(map_)
    
    folium.Marker(
    location=[ 50.4398, 4.4331],
    popup="Minérale",
    icon=folium.Icon(color="red"),
    ).add_to(map_)
    ## add points
    routes = []
    i = 0
    for t in trucks:
        i += 1
        locs = []
        long.append([])
        lat.append([])
        if t.is26T:
            flat = t.route
        else:
            if t.route[0].Id == -1: # avant 596
                flat = [t.route[0]] + [x for x in t.route[1]] + [x for x in t.route[2]]+ [t.route[-2]] +[t.route[-1]]
            else:
                flat = [t.route[0]] + [x for x in t.route[1]] + [x for x in t.route[2]]+ [t.route[-1]]
            if len(flat) == 3:
                flat = [item for sublist in flat for item in sublist]
        # #print("flat is ", flat)
        for glass_bin in flat:
            if type(glass_bin) == int:
                loc = [depot.latitude, depot.latitude]
            else:
                # #print("glass bin is ", glass_bin)
                if glass_bin.Id != -2 and glass_bin.Id != -1 and glass_bin.Id != -3:
                    loc = [DicoBulles[glass_bin.Id].latitude, DicoBulles[glass_bin.Id].longitude]
                elif glass_bin.Id == -3:
                    loc = [50.4398, 4.4331]
                elif glass_bin.Id == -2:
                    loc = [50.725, 3.32114]
                elif glass_bin.Id == -1:
                    loc = [ 50.3690,  3.9670]
                folium.Marker(
                    location=loc, 
                    popup="Bulle N : \t" +str(glass_bin.Id) + "</br>Poids : \t" + str(round(glass_bin.poids, 2)) + " kg",
                    color=lst_colors[color_index], fill=True,
                    radius=5).add_to(map_)
                legend_html = legend_html+"""&nbsp;<i class="fa fa-circle 
                fa-1x" style="color:"""+lst_colors[color_index]+"""">
                </i>&nbsp;"""+str(glass_bin)+"""<br>"""
                    
            locs.append(loc)
        
        if not t.is26T:
            if t.route[0].Id == -1:
                my_PolyLine=folium.PolyLine(locations=locs[0:2], color=lst_colors[color_index],weight=3)
                map_.add_child(my_PolyLine)
                my_PolyLine=folium.PolyLine(locations=locs[1:len(t.route[1])+1], color=lst_colors[color_index+1],weight=3)
                map_.add_child(my_PolyLine)
                my_PolyLine=folium.PolyLine(locations=locs[len(t.route[1])+1:len(t.route[1])+1+len(t.route[2])], color=lst_colors[color_index+2],weight=3)
                map_.add_child(my_PolyLine)
                my_PolyLine=folium.PolyLine(locations=locs[-2:], color=lst_colors[color_index],weight=3)
                map_.add_child(my_PolyLine)
            else:
                my_PolyLine = folium.PolyLine(locations=locs[0:2], color=lst_colors[color_index], weight=3)
                map_.add_child(my_PolyLine)
                my_PolyLine = folium.PolyLine(locations=locs[1:len(t.route[1]) + 1], color=lst_colors[color_index + 1],
                                              weight=3)
                map_.add_child(my_PolyLine)
                my_PolyLine = folium.PolyLine(locations=locs[len(t.route[1]) + 1:len(t.route[1]) + 1 + len(t.route[2])],
                                              color=lst_colors[color_index + 2], weight=3)
                map_.add_child(my_PolyLine)
                my_PolyLine = folium.PolyLine(locations=locs[-3:], color=lst_colors[color_index], weight=3)
                map_.add_child(my_PolyLine)
        else:
            # #print("locs is ", locs)
            my_PolyLine=folium.PolyLine(locations=locs, color=lst_colors[color_index],weight=3)
            map_.add_child(my_PolyLine)
        color_index += 1
        if color_index > len(lst_colors)-3:
            color_index -= len(lst_colors)
    ## add html legend
    legend_html = legend_html+"""</div>"""
    map_.get_root().html.add_child(folium.Element(legend_html))
    
    ## plot the map
    map_
    map_.save(outfile=outf)

def plotCluster(df, outf):
    lst_colors=[ 'black', 'orange', 'pink', 'purple', 'red','lightgreen', 'blue','green', 'darkblue', 'darkgreen', 'darkpurple', 'darkred', 'gray', 'lightblue', 'lightgray',  'lightred']
    legend_html = """<div style="position:fixed; bottom:10px; left:10px; border:2px solid black; z-index:9999; font-size:14px;">&nbsp;<b>test:</b><br>"""

    map_ = folium.Map(location=[df.iloc[0].Latitude, df.iloc[0].Longitude], tiles="cartodbpositron",
                      zoom_start=10)
    
    folium.Marker(
    location=[ 50.7250, 3.3211],
    popup="Dottignies",
    icon=folium.Icon(color="green"),
    ).add_to(map_)
    
    folium.Marker(
    location=[ 50.3690,  3.9670],
    popup="Quevy",
    icon=folium.Icon(color="blue"),
    ).add_to(map_)
    
    folium.Marker(
    location=[ 50.4398, 4.4331],
    popup="Minérale",
    icon=folium.Icon(color="red"),
    ).add_to(map_)
    
    
    for index, row in df.iterrows():
        loc = [row["Latitude"], row["Longitude"]]
        color_idx = int(row["cluster"])
        if color_idx > len(lst_colors)-1:
            color_idx -= len(lst_colors)
        folium.CircleMarker(
            location=loc, 
            # popup=str(row["Latitude"]) + "</br>" + str(row["Longitude"]),
            
            popup=str(row["bin_index"])+"</br>"+str(row["Latitude"]) + "</br>" + str(row["Longitude"]),
            color=lst_colors[color_idx], fill=True,
            radius=5).add_to(map_)
        legend_html = legend_html+"""&nbsp;<i class="fa fa-circle 
        fa-1x" style="color:"""+lst_colors[color_idx]+"""">
        </i>&nbsp;"""+str(index)+"""<br>"""
    
    
    legend_html = legend_html+"""</div>"""
    map_.get_root().html.add_child(folium.Element(legend_html))
    map_
    map_.save(outfile=outf)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    