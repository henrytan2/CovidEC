from django.http import HttpResponse
from django.views import generic
import pandas as pd
from selenium import webdriver
import json
from pyvirtualdisplay import Display


class IndexView(generic.TemplateView):
    template_name = "index.html"

    def post(self, request):
        if request.method == 'POST':
            with Display():
                driver = webdriver.Firefox()
                driver.get("http://google.org/crisisresponse/covid19-map?hl=en-US")

                html = driver.page_source
                # Get HTML from page and parse it into a pandas DataFrame
                data = pd.read_html(html, match="Location")[0]

                # Replace dashes with numpy.nan
                data.replace('—', 0, inplace=True)

                # Now we calculate the percentage of people recovered or... otherwise
                recoveredOverConfirmed = []
                deathsOverConfirmed = []
                for index, row in data.iterrows():
                    try:
                        recoveredOverConfirmed.append(
                            str(int(float(row['Recovered']) / row['Confirmed'] * 100)) + "%")
                    except ValueError:
                        recoveredOverConfirmed.append(0)
                    except ZeroDivisionError:
                        recoveredOverConfirmed.append(0)

                    try:
                        deathsOverConfirmed.append(str(int(float(row['Deaths']) / row['Confirmed'] * 100)) + "%")
                    except ValueError:
                        deathsOverConfirmed.append(0)
                    except ZeroDivisionError:
                        deathsOverConfirmed.append(0)

                # Now we insert two new columns with the new data
                data.insert(len(data.columns), "Recovered %", recoveredOverConfirmed, True)
                data.insert(len(data.columns), "Dead %", deathsOverConfirmed, True)
                data_dict = data.to_dict(orient='records')
                data_json = json.dumps(data_dict)
            return HttpResponse(data_json)
