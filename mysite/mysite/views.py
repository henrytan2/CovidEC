from django.http import HttpResponse
from django.views import generic
import pandas as pd
import numpy as np


class IndexView(generic.TemplateView):
    template_name = "index.html"

    def post(self, request):
        if request.method == 'POST':
            # get html from google and store in pandas dataframe
            data = pd.read_html("http://google.org/crisisresponse/covid19-map?hl=en-US", match="Location")[0]

            # below is used to calculate the percentages of recovered and dead
            recovered_percent = []
            deaths_percent = []

            # iterate through the rows to calculate the percentages
            for index, row in data.iterrows():
                try:
                    recovered_percent.append(
                        str(int(float(row['Recovered']) / row['Confirmed cases'] * 100)) + "%")
                except ValueError:
                    recovered_percent.append(np.nan)
                except ZeroDivisionError:
                    recovered_percent.append(0)

                try:
                    deaths_percent.append(str(int(float(row['Deaths']) / row['Confirmed cases'] * 100)) + "%")
                except ValueError:
                    deaths_percent.append(np.nan)
                except ZeroDivisionError:
                    deaths_percent.append(0)

            # Now we insert two new columns with the new data
            data.insert(len(data.columns), "Recovered %", recovered_percent, True)
            data.insert(len(data.columns), "Dead %", deaths_percent, True)

            data_json = data.to_json()
            return HttpResponse('index', {'covid_data': data_json})
