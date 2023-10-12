    
def Bokeh_Clustering_Code():
    global mix3, color_mapper, axis_keys
    mix3, color_mapper, axis_keys = None, None, None

    def modify_doc(doc):

        options_to_select = [ "Median household income 2019", "Per capita income 2019",
                "Mean household income 2019", "Avg family size 2019", "% Unemployment rate 2017", "% Broadband 2017"
                , "% Bachelors 2019", "% White 2019", "% Black 2019", "% Native 2019", "% Asian 2019", "% Hispanic 2019"
                , "Median age 2019", "% High school grad 2019", "% Uninsured 2019", '% of votes for Trump',
        '% of votes for Jorgensen', '% of votes for Biden', '% of votes for Others']
        
        df_keys = [ "median_household_income_2019", "per_capita_income_2019",
                "mean_household_income_2019", "avg_family_size_2019", "unemployment_rate_2017", "broadband_2017"
                , "bachelors_2019", "white_2019", "black_2019", "native_2019", "asian_2019", "hispanic_2019"
                , "median_age_2019", "hs_grad_2019", "uninsured_2019", 'share_of_votes_TRUMP',
        'share_of_votes_JORGENSEN', 'share_of_votes_BIDEN', 'share_of_votes_OTHER']
        
        cluster_options = list(range(1,11))
        
        refresh  = Button(label = "Refresh")
        dropdown = Select(title="X-axis metric", value= '% of votes for Biden', options=options_to_select, width = 200)
        dropdown2 = Select(title="Y-axis metric", value= "Per capita income 2019", options=options_to_select, width = 200)
        
        cluster_slider = Slider(start=2, end=10, value=5, step=1, title="Select the number of clusters", width = 150)
        
        multi_select = MultiSelect(title = "Select categories to cluster on", value=options_to_select , options= options_to_select, width = 200, height = 170)
        cluster_select = MultiSelect(title = "Select visible clusters", value=list(str(i) for i in cluster_options[0:cluster_slider.value]) , options= list(str(i) for i in cluster_options[0:cluster_slider.value]) , width = 200, height = 170)
        
        TOOLS = "pan,wheel_zoom,reset,hover,save,lasso_select,box_select"
        
        clustering_algos = [cluster.KMeans, cluster.Birch, cluster.MeanShift, cluster.SpectralClustering, cluster.AgglomerativeClustering]
        clustering_algos_names = ["KMeans", "Birch", "Mean Shift", "Spectral", "Agglomerative"]
        algo_select = Select(title="Select clustering method", value="KMeans", options=clustering_algos_names, width = 200)
        # Initialize our plot figure
        p = figure(title="U.S. counties clustered by selection.", plot_height = 400, width = 600, tools = TOOLS)

        p2 = figure(title="Scatter plot of U.S. counties", plot_height = 400, width = 375, tools = TOOLS)
        
        def set_cluster_algo(choice, n_clusters):
            method = clustering_algos[clustering_algos_names.index(choice)]
            if choice == "Birch":
                return clustering_algos[clustering_algos_names.index(choice)](n_clusters = n_clusters )
            if choice == "KMeans":
                return clustering_algos[clustering_algos_names.index(choice)](n_clusters = n_clusters, init = 'random')
            if choice == "Mean Shift":
                return clustering_algos[clustering_algos_names.index(choice)](bandwidth=2, cluster_all = False)
            if choice == "Spectral":
                return clustering_algos[clustering_algos_names.index(choice)](n_clusters = n_clusters)
            if choice == "Agglomerative":
                return clustering_algos[clustering_algos_names.index(choice)](n_clusters = n_clusters)
        
        def means(frame):
            return pd.DataFrame(frame).groupby(by = "clusters").mean()
        
        
        # set a color mapper that uses the red-to-green palette, make missing data dark grey
        def set_pallete(low, high):
            #return LinearColorMapper(field_name = dropdown.value, palette = Spectral6, low = low, high = high, nan_color = '#838383')
            return linear_cmap(field_name = "clusters", palette = Plasma256, low = low, high = high, nan_color = '#838383')
        
        def get_technical_keys(category_names):
            return [df_keys[options_to_select.index(i)] for i in category_names]
        
        global axis_keys
        axis_keys = get_technical_keys([dropdown.value, dropdown2.value])

        def add_hover(fig):
            fig.add_tools(HoverTool(tooltips=[("Name", "@name"),("Cluster", "@clusters"), (f"{dropdown.value}", f"@{axis_keys[0]}")
                                    , (f"{dropdown2.value}", f"@{axis_keys[1]}") ]))
        #add tooltips
        add_hover(p)
        add_hover(p2)
        
        cluster_algo = set_cluster_algo(algo_select.value, cluster_slider.value)
        
        update_keys = get_technical_keys([dropdown.value, dropdown2.value])
        
        
        df1 = pd.read_csv("US_demographic_and_election_data_per_county_part1.csv")
        df1 = pd.read_csv("US_demographic_and_election_data_per_county_part2.csv")
        mix2 = pd.concat([df1,df2]).fillna(0)

        y_cluster = cluster_algo.fit_predict(sc.fit_transform(mix2[update_keys].values)) + 1
        mix2["clusters"] = y_cluster
        
        geo_src = bm.GeoJSONDataSource(geojson=mix2[~mix2.state_x.isin(["hawaii", "alaska"])][["geometry","name","clusters"] + update_keys].to_json())
        global mix3
        mix3 = mix2[~mix2.state_x.isin(["hawaii", "alaska"])][["geometry","name","clusters"] + update_keys]
        global color_mapper
        color_mapper = set_pallete(1, cluster_slider.value)
        
        u = p.patches('xs','ys', source = geo_src, #fill_color = dropdown.value,
                color = color_mapper, line_color = 'black', line_width = 0.25, fill_alpha = 1
            )
        
        p2.circle(update_keys[0], update_keys[1], source = geo_src
                , size = 10
                , line_color="black"
                , fill_color=color_mapper
            )    
        
        #replace axis labels and set start rango at 0
        p2.xaxis.axis_label = dropdown.value
        p2.yaxis.axis_label = dropdown2.value
        p2.x_range.start =  0
        p2.y_range.start =  0

        def update_data():
            #re-cluster dataframe based on selected parameters
            cluster_algo = set_cluster_algo(algo_select.value, cluster_slider.value)
            
            update_keys = get_technical_keys(multi_select.value)
            global axis_keys
            axis_keys = get_technical_keys([dropdown.value, dropdown2.value])
            
            mix2_clusters = mix2[update_keys].values
            y_cluster = cluster_algo.fit_predict(sc.fit_transform(mix2[update_keys].values)) + 1
            mix2["clusters"] = y_cluster
        
            #final data to be visualized and turned into JSON
            global mix3
            mix3 = mix2[~mix2.state_x.isin(["hawaii", "alaska"])][["geometry","name","clusters"] + list(set(update_keys + axis_keys))]       
            result = bm.GeoJSONDataSource(geojson=mix3.to_json())
            
            #adjust color mapper and update glyph fill colors
            global color_mapper
            color_mapper = set_pallete(1, cluster_slider.value)
            u.glyph.fill_color = color_mapper
            
            p2.circle(axis_keys[0], axis_keys[1], source = geo_src
                , size = 10
                , line_color="black"
                , fill_color=color_mapper
            )   
    
            #replace Geo JSON data
            geo_src.geojson = result.geojson
            
            #replace axis labels
            p2.xaxis.axis_label = dropdown.value
            p2.yaxis.axis_label = dropdown2.value
            p2.x_range.end, p2.y_range.end =  mix3[axis_keys[0]].max() *1.05, mix3[axis_keys[1]].max() *1.05
            p2.xaxis[0].formatter = NumeralTickFormatter(format="0.")
            p2.yaxis[0].formatter = NumeralTickFormatter(format="0.")
            
            #update number of clusters in cluster selector
            cluster_select.value = list(str(i) for i in cluster_options[0:cluster_slider.value])
            cluster_select.options = list(str(i) for i in cluster_options[0:cluster_slider.value])
            
            add_hover(p)
            add_hover(p2)
            
        def filter_cluster(attr, old, new):
            mix_fl = mix3[mix3.clusters.isin([int(i) for i in cluster_select.value])]
            result = bm.GeoJSONDataSource(geojson=mix_fl.to_json())
            #replace Geo JSON data
            geo_src.geojson = result.geojson
            
            #update scatter plot ranges
            p2.x_range.end, p2.y_range.end =  np.round(mix3[axis_keys[0]].max() *1.05,2), np.round(mix3[axis_keys[1]].max() *1.05,2)
            #p2.xaxis[0].formatter = NumeralTickFormatter(format="0.")
            #p2.yaxis[0].formatter = NumeralTickFormatter(format="0.")
                
        #refesh data with on click action
        refresh.on_click( update_data)
        cluster_select.on_change("value", filter_cluster)
        
        p.y_range = Range1d(23,50)
        p.x_range = Range1d(-127,-66)
        
        layout = row(column(row(column(refresh, cluster_slider), column(dropdown, dropdown2, algo_select), column(cluster_select), multi_select), row(p, p2)))

        # add the layout to curdoc
        doc.add_root(layout)
        
    #show the doc
    show(modify_doc)