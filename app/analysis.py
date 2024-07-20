# from matplotlib import pyplot
# import seaborn
import pandas
import numpy
from collections import defaultdict
from . import models
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from random import random
from sklearn.svm import OneClassSVM
from scipy.stats import pareto, gamma
from datetime import date

# import requests
# from requests.auth import HTTPBasicAuth
# add file path of your own system
# filename = "D:/analytics_api/analytics_api/ai_top40.csv"


class Analysis:
    def __init__(self):
        self.file_name = ""
        self.data = []
        # self.artists = []
        self.tempTable = models.TemporaryTable

    def get_file_name(self):
        self.file_name = self.tempTable.get_file_name()
        if self.file_name:
            # print(self.data)
            return self.file_name

    def display_table(self):
        self.data = pandas.DataFrame(self.tempTable.get_json_data())
        if not self.data.empty:
            # print(self.data)
            return self.data.to_json(orient="split")

    # def get_artist_barchart_data(self):
    #     # count songs per artist
    #     self.artists = defaultdict(int)
    #     for i, song in self.data.iterrows():
    #         for musician in song["Artist Name(s)"].split(","):
    #             self.artists[musician] += 1

    #     # sort for chart
    #     self.artists = (
    #         pandas.DataFrame(self.artists.items(), columns=["Artist", "Num Songs"])
    #         .sort_values("Num Songs", ascending=False)
    #         .reset_index(drop=True)
    #     )
    #     return self.artists.to_json(orient="split")

    # def get_volume_added_overtime(self):
    #     parse_date = lambda d: (int(d[:4]), int(d[5:7]), int(d[8:10]))
    #     songs = self.data
    #     dates = [date(*parse_date(d)) for d in songs["Added At"]]
    #     return dates

    def analyse_csv(self):
        if not isinstance(self.data, pandas.DataFrame):
            self.data = pandas.DataFrame(self.tempTable.get_json_data())
        # count songs per artist
        artists = defaultdict(int)
        for i, song in self.data.iterrows():
            for musician in song["Artist Name(s)"].split(","):
                artists[musician] += 1

        # sort for chart
        artists = (
            pandas.DataFrame(artists.items(), columns=["Artist", "Num Songs"])
            .sort_values("Num Songs", ascending=False)
            .reset_index(drop=True)
        )

        ####################################################
        artists_barchart = artists.to_json(orient="values")
        ###################################################

        # Let's find the best parameters. Need x, y data 'sampled' from the distribution for
        # parameter fit.
        y = []
        for i in range(artists.shape[0]):
            for j in range(artists["Num Songs"][i]):
                y.append(i)  # just let y have index[artist] repeated for each song

        # sanity check. If the dataframe isn't sorted properly, y isn't either.
        # pyplot.figure()
        # pyplot.hist(y, bins=30)

        # The documentation is pretty bad, but this is okay:
        # https://stackoverflow.com/questions/6620471/fitting-empirical-distribution-to-theoretical-
        # ones-with-scipy-python
        param = pareto.fit(y, 100)
        pareto_fitted = len(y) * pareto.pdf(range(artists.shape[0]), *param)

        ###############################################
        everybody_artist_barchart = pareto_fitted  # send as is because array
        ###########################################

        # param = gamma.fit(y) # gamma fits abysmally; see for yourself by uncommenting
        # gamma_fitted = len(y)*gamma.pdf(range(artists.shape[0]), *param)

        ###########################################
        top50_artists_barchart = artists[:50].to_json(orient="values")
        ###################################################

        parse_date = lambda d: (int(d[:4]), int(d[5:7]), int(d[8:10]))
        songs = self.data
        dates = [date(*parse_date(d)) for d in songs["Added At"]]

        #################################################
        volume_added_overtime = dates
        #################################################

        # bar chart of first bar chart == hipster diversity factor
        frequency = defaultdict(int)
        for n in artists["Num Songs"]:
            frequency[n] += n
        frequency = pandas.DataFrame(
            frequency.items(), columns=["Unique Count", "Volume"]
        ).sort_values("Volume", ascending=False)
        # print(
        #     "number of song-artist pairs represented in the eclecticness chart:",
        #     sum(frequency["Volume"]),
        # )

        #########################################################
        volume_of_songs = frequency.to_json(orient="values")
        #####################################################

        # count songs per genre
        genres = defaultdict(int)
        for i, song in self.data.iterrows():
            if (
                type(song["Genres"]) is str
            ):  # some times there aren't any, and this is NaN
                for genre in song["Genres"].split(","):
                    if len(genre) > 0:  # empty string seems to be a legit genre
                        genres[genre] += 1

        # sort for chart
        genres = (
            pandas.DataFrame(genres.items(), columns=["Genre", "Num Songs"])
            .sort_values("Num Songs", ascending=False)
            .reset_index(drop=True)
        )

        #############################################################
        all_genres = genres.to_json(orient="values")
        #############################################################

        y = []
        for i in range(genres.shape[0]):
            for j in range(genres["Num Songs"][i]):
                y.append(i)

        # sanity check
        # pyplot.figure()
        # pyplot.hist(y, bins=30)

        param = pareto.fit(y, 100)

        #############################################################
        pareto_fitted_genres = len(y) * pareto.pdf(range(genres.shape[0]), *param)
        #############################################################

        years = defaultdict(int)
        for i, song in self.data.iterrows():
            years[song["Release Date"][:4]] += 1

        years = pandas.DataFrame(
            years.items(), columns=["Year", "Num Songs"]
        ).sort_values("Year")

        #############################################################
        songs_per_year = years.to_json(orient="values")
        #############################################################

        # Some years are missing, so transform to a dataframe that covers full time period.
        eldest = int(years["Year"].values[0])
        youngest = int(years["Year"].values[-1])
        missing_years = [
            str(x)
            for x in range(eldest + 1, youngest)
            if str(x) not in years["Year"].values
        ]
        ago = (
            pandas.concat(
                [
                    years,
                    pandas.DataFrame.from_dict(
                        {
                            "Year": missing_years,
                            "Num Songs": [0 for x in range(len(missing_years))],
                        }
                    ),
                ]
            )
            .sort_values("Year", ascending=False)
            .reset_index(drop=True)
        )

        #######################################################
        songs_per_year_absolute = ago.to_json(orient="values")
        #######################################################
        y = []
        for i in range(ago.shape[0]):
            for j in range(int(ago["Num Songs"][i])):
                y.append(i)

        # sanity check histogram to make sure I'm constructing y properly
        # pyplot.figure()
        # pyplot.hist(y, bins=30)

        param = gamma.fit(y, 10000)

        #######################################################
        gamma_fitted_songs_per_year = len(y) * gamma.pdf(range(ago.shape[0]), *param)
        #######################################################

        ################ Poppularity Contest #############
        popularity = defaultdict(int)
        for i, song in self.data.iterrows():
            popularity[song["Popularity"]] += 1

        popularity = pandas.DataFrame(
            popularity.items(), columns=["Popularity", "Num Songs"]
        ).sort_values("Popularity")

        ###########################################
        poppularity_distribution = popularity.to_json(orient="values")
        ###########################################

        # Musical features
        musical_features = {}
        for i, category in enumerate(
            [
                "Tempo",
                "Acousticness",
                "Instrumentalness",
                "Liveness",
                "Valence",
                "Speechiness",
                "Loudness",
                "Energy",
                "Danceability",
            ]
        ):
            musical_features[category] = self.data[category].tolist()

        # Other features
        other_features = {}
        for i, category in enumerate(
            [
                "Time Signature",
                "Key",
                "Mode",
            ]
        ):
            other_features[category] = self.data[category].tolist()

        # Data for frontier Plot
        numerical_data = self.data.drop(
            [
                "Spotify ID",
                "Artist IDs",
                "Track Name",
                "Album Name",
                "Artist Name(s)",
                "Added By",
                "Added At",
                "Genres",
            ],
            axis=1,
        )
        numerical_data["Release Date"] = pandas.to_numeric(
            numerical_data["Release Date"].str.slice(0, 4)
        )
        for column in numerical_data:
            numerical_data[column] = pandas.to_numeric(numerical_data[column])
        # print(numerical_data.mean())
        numerical_data = (
            numerical_data - numerical_data.mean(axis=0)
        ) / numerical_data.std()

        tsne_embedded = TSNE(n_components=2).fit_transform(numerical_data)

        svm_tsne = OneClassSVM(gamma="scale")
        svm_tsne.fit(tsne_embedded)
        # plotFrontier(tsne_embedded, svm_tsne, 't-SNE', 1.2)
        # get all the points in the space, and query the svm on them
        scale = 1.2
        xx, yy = numpy.meshgrid(
            numpy.linspace(
                min(tsne_embedded[:, 0]) * scale, max(tsne_embedded[:, 0]) * scale, 500
            ),
            numpy.linspace(
                min(tsne_embedded[:, 1]) * scale, max(tsne_embedded[:, 1]) * scale, 500
            ),
        )
        Z = svm_tsne.decision_function(numpy.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)  # positive Z means yes. negative means outliers.
        levels = numpy.linspace(Z.min(), 0, 8).tolist()
        print(Z.max())
        station_fit_score_t_sine = {
            "embedded_x": tsne_embedded[:, 0].tolist(),
            "embedded_y": tsne_embedded[:, 1].tolist(),
            "xx": numpy.linspace(-2, 3, 500).tolist(),
            "yy": numpy.linspace(-2, 3, 500).tolist(),
            "Z": Z.tolist(),
            "level_start": levels[0],
            "level_end": 0,
            "level_size": (levels[1] - levels[0]),
            "zmax": Z.max(),
            "songs": self.data["Track Name"].tolist(),
        }

        pca = PCA(n_components=2)
        pca_embedded = pca.fit_transform(numerical_data)
        print(
            "% variance explained by successive PCA dimensions:",
            pca.explained_variance_ratio_,
        )

        svm_pca = OneClassSVM(gamma="scale")
        svm_pca.fit(pca_embedded)

        # plotFrontier(pca_embedded, svm_pca, 'PCA', 1)
        # get all the points in the space, and query the svm on them
        scale = 1
        xx, yy = numpy.meshgrid(
            numpy.linspace(
                min(pca_embedded[:, 0]) * scale, max(pca_embedded[:, 0]) * scale, 500
            ),
            numpy.linspace(
                min(pca_embedded[:, 1]) * scale, max(pca_embedded[:, 1]) * scale, 500
            ),
        )
        Z = svm_pca.decision_function(numpy.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)  # positive Z means yes. negative means outliers.
        levels = numpy.linspace(Z.min(), 0, 8).tolist()
        print(Z.max())
        station_fit_score_pca = {
            "embedded_x": pca_embedded[:, 0].tolist(),
            "embedded_y": pca_embedded[:, 1].tolist(),
            "xx": numpy.linspace(-4, 4, 500).tolist(),
            "yy": numpy.linspace(-4, 4, 500).tolist(),
            "Z": Z.tolist(),
            "level_start": levels[0],
            "level_end": 0,
            "level_size": (levels[1] - levels[0]),
            "zmax": Z.max(),
            "songs": self.data["Track Name"].tolist(),
        }

        output = {
            "artists_barchart": artists_barchart,
            "everybody_artist_barchart": everybody_artist_barchart.tolist(),
            "top50_artists_barchart": top50_artists_barchart,
            "volume_added_overtime": volume_added_overtime,
            "volume_of_songs": volume_of_songs,
            "all_genres": all_genres,
            "pareto_fittred_genres": pareto_fitted_genres.tolist(),
            "songs_per_year": songs_per_year,
            "songs_per_year_absolute": songs_per_year_absolute,
            "gamma_fitted_songs_per_year": gamma_fitted_songs_per_year.tolist(),
            "popularity_distribution": poppularity_distribution,
            "histogram_of_songs_length": (
                self.data["Duration (ms)"].astype(int) / 1000
            ).tolist(),
            "musical_features": musical_features,
            "other_features": other_features,
            "station_fit_score_t_sine": station_fit_score_t_sine,
            "station_fit_score_pca": station_fit_score_pca,
        }
        return output

    # def plotFrontier(embedded, svm, technique_name, scale):
    #     # get all the points in the space, and query the svm on them
    #     xx, yy = numpy.meshgrid(numpy.linspace(min(embedded[:,0])*scale,
    #                                         max(embedded[:,0])*scale, 500),
    #                             numpy.linspace(min(embedded[:,1])*scale,
    #                                         max(embedded[:,1])*scale, 500))
    #     Z = svm.decision_function(numpy.c_[xx.ravel(), yy.ravel()])
    #     Z = Z.reshape(xx.shape) # positive Z means yes. negative means outliers.

    #     pyplot.figure(figsize=(20,20))
    #     pyplot.title('Station Fit Score')
    #     pyplot.contourf(xx, yy, Z, levels=numpy.linspace(Z.min(), 0, 8), cmap=pyplot.cm.Blues_r)
    #     pyplot.contour(xx, yy, Z, levels=[0], linewidths=2, colors='green') # the +/- boundary
    #     pyplot.contourf(xx, yy, Z, levels=[0, Z.max()], colors='lightgreen')

    #     pyplot.scatter(embedded[:, 0], embedded[:, 1], s=10, c='grey')
    #     for i,song in data.iterrows():
    #         #if random() < show_percent*0.01: # randomly label % of points
    #         #if song['Artist Name(s)'] in ['Coldplay']:
    #             x, y = embedded[i]
    #             pyplot.annotate(song['Track Name'], (x,y), size=10,
    #                 xytext=(-30,30), textcoords='offset points',
    #                 ha='center',va='bottom',
    #                 arrowprops={'arrowstyle':'->', 'color':'red'})


# if __name__ == "__main__":
#     x = Analysis()
#     x.display_table()
