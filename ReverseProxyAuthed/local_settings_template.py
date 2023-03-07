RPA_REVERSE_API_URLS = {
    'cds-uid': r"",
    'tds-nwk': r""
}
RPA_AVAILABLE_SERVICES = {
    "get-netcdf-data": "{}/get-netcdf-data/".format(RPA_REVERSE_API_URLS['cds-uid']),
    "MET-WMS": "{}thredds/wms/MET/summaries/".format(RPA_REVERSE_API_URLS['tds-nwk'])
}