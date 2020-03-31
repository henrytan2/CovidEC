from django.http import HttpResponse
from django.views import generic
import pandas as pd
import json


class IndexView(generic.TemplateView):
    template_name = "index.html"

    def post(self, request):
        if request.method == 'POST':
            # get html table from source
            data = pd.read_html("https://google.org/crisisresponse/covid19-map/index/Table/1?hl=en-US", match="Location")[0]

            # replace non-numbers wqith 0
            data.replace('â', 0, inplace=True)
            data.replace("—", 0, inplace=True)

            # Now we calculate the percentage of people recovered or... otherwise
            recovered_percent = []
            deaths_percent = []
            for index, row in data.iterrows():
                try:
                    recovered_percent.append(
                        str(int(float(row['Recovered']) / row['Confirmed cases'] * 100)) + "%")
                except ValueError:
                    recovered_percent.append(0)
                except ZeroDivisionError:
                    recovered_percent.append(0)

                try:
                    deaths_percent.append(str(int(float(row['Deaths']) / row['Confirmed cases'] * 100)) + "%")
                except ValueError:
                    deaths_percent.append(0)
                except ZeroDivisionError:
                    deaths_percent.append(0)

            # insert the calculated columns to dataframe
            data.insert(len(data.columns), "Recovered %", recovered_percent, True)
            data.insert(len(data.columns), "Dead %", deaths_percent, True)
            data_dict = data.to_dict(orient='records')
            data_json = json.dumps(data_dict)
            return HttpResponse(data_json)
