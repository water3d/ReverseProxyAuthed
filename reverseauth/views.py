from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import requests

from ReverseProxyAuthed.settings import RPA_AVAILABLE_SERVICES

# Create your views here.

def test(request):
	params = {
		"decimal-precision": 2,
		"lat": 38.5455,
		"lon": -121.5053,
		"positive-east-longitude": False,
		"request-JSON": True,
		"data-path": ["/datastore-reacch/MET/climatologies/gridmet_vs_Jan1_dailyPercentiles_p10.nc", "/datastore-reacch/MET/climatologies/gridmet_vs_Jan1_dailyPercentiles_p90.nc"],
		"variable": ["p10","p90"],
		"variable-name": ["p10", "p90"]
	}

	params2 = [("decimal-precision", "2"),
		("lat", "46.7324"),
		("lon", "-117.0002"),
		("positive-east-longitude", "False"),
		("data-path", "/reacch-data/MET/data/spi14d.nc"),
		("variable", "spi"),
		("variable-name", "spi14d"),
		("data-path", "/reacch-data/MET/data/spi30d.nc"),
		("variable", "spi"),
		("variable-name", "spi30d"),
		("data-path", "/reacch-data/MET/data/spi90d.nc"),
		("variable", "spi"),
		("variable-name", "spi90d"),
		("data-path", "/reacch-data/MET/data/spi180d.nc"),
		("variable", "spi"),
		("variable-name", "spi180d"),
		("data-path", "/reacch-data/MET/data/spi270d.nc"),
		("variable", "spi"),
		("variable-name", "spi270d"),
		("data-path", "/reacch-data/MET/data/spi1y.nc"),
		("variable", "spi"),
		("variable-name", "spi1y"),
		("data-path", "/reacch-data/MET/data/spi2y.nc"),
		("variable", "spi"),
		("variable-name", "spi2y"),
		("data-path", "/reacch-data/MET/data/spi5y.nc"),
		("variable", "spi"),
		("variable-name", "spi5y"),
		("request-JSON", "True")
	]
	test_url = "{}/get-netcdf-data/?".format(RPA_AVAILABLE_SERVICES['get-netcdf-data'])
	response = requests.get(test_url, params2)
	print(response.url)
	return HttpResponse(response.content, content_type="application/json")



class MainPassthroughAPIView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request, **kwargs):
		service = kwargs['service']
		if service not in RPA_AVAILABLE_SERVICES:
			resp = HttpResponse("Requested service {} is not available on this server".format(service))
			resp.status_code=404
			return resp
		base_url = RPA_AVAILABLE_SERVICES[service]

		# Step 1: Check that the user is authorized. Send the request object, the service, and the params through
		# so we can make sure they're allowed to send this request
		auth_data = _check_auth(request, service, query_string=request.META['QUERY_STRING'])
		if not auth_data['authed']:
			return auth_data['response']# TODO: Make this return an HTTPResponse with the right information. Maybe DRF can help, or maybe we do this manually to keep it lean.

		# Step 2: Craft and send the request
		url = "{}/{}/?{}".format(base_url, service, request.META['QUERY_STRING'])
		response = requests.get(url, stream=True)
		print(response.url)

		# Step 2b: If we anticipate the server will open a stream with us to send a ton of data, we should probably do the
		# same on our end to stream data straight through to the end user (e.g. we'll read the buffer, immediately send it
		# through, then read some more. This will be a bit slow for the end user, but can be optimized - we read some chunks,
		# then send those chunks through - we might also be able to handle it with async/await, or spin off a subprocess.
		# should be able to feed the streaming body from requests into a StreamingHTTPResponse object from Django.
		# TODO: See above - we are currently streaming data by default below

		# Step 3: Craft the response.
		# TODO: We should return the same HTTP status code as the server sends to us
		resp = StreamingHttpResponse(response.iter_lines(), content_type="application/json")
		resp.status_code=response.status_code
		return resp


def _check_auth(request, service, query_string=None):
	# TODO: For now, just being authenticated is enough. But at some point we'll want more
	return {'authed': True}