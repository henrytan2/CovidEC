from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic
import pandas as pd
import numpy as np
import requests


class IndexView(generic.TemplateView):
    template_name = "index.html"

    def post(self, request):
        if request.method == 'POST':
            # Get HTML from page and parse it into a pandas DataFrame
            data = pd.read_html("http://google.org/crisisresponse/covid19-map?hl=en-US", match="Location")[0]

            # Replace dashes with numpy.nan
            data.replace('—', "nan", inplace=True)

            # Convert "Cases per 1M people" column to numbers for sorting
            data["Cases per 1M people"] = pd.to_numeric(data["Cases per 1M people"])

            # Now we calculate the percentage of people recovered or... otherwise
            recoveredOverConfirmed = []
            deathsOverConfirmed = []
            for index, row in data.iterrows():
                try:
                    recoveredOverConfirmed.append(
                        str(int(float(row['Recovered']) / row['Confirmed cases'] * 100)) + "%")
                except ValueError:
                    recoveredOverConfirmed.append(np.nan)
                except ZeroDivisionError:
                    recoveredOverConfirmed.append(0)

                try:
                    deathsOverConfirmed.append(str(int(float(row['Deaths']) / row['Confirmed cases'] * 100)) + "%")
                except ValueError:
                    deathsOverConfirmed.append(np.nan)
                except ZeroDivisionError:
                    deathsOverConfirmed.append(0)

            # Now we insert two new columns with the new data
            data.insert(len(data.columns), "Recovered %", recoveredOverConfirmed, True)
            data.insert(len(data.columns), "Dead %", deathsOverConfirmed, True)

            data_json = data.to_json()
            return HttpResponse('index', {'covid_data': data_json})
