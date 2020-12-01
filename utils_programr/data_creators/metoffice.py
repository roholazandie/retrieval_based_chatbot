import os

import metoffer

from programr.utils.weather.metoffice import MetOffice

if __name__ == '__main__':

    # Only to be used to create test data for unit aiml_tests

    from programr.utils.license.keys import LicenseKeys

    license_keys = LicenseKeys()
    license_keys.load_license_key_file(os.path.dirname(__file__) + '/../../../../bots/y-bot/config/license.keys')

    met_office = MetOffice(license_keys)

    lat = 56.0720397
    lng = -3.1752001

    log_to_file = False

    if log_to_file:
        met_office.nearest_location_observation_to_file(lat, lng, "observation.json")
        met_office.nearest_location_forecast_to_file(lat, lng, metoffer.DAILY, "forecast_daily.json")
        met_office.nearest_location_forecast_to_file(lat, lng, metoffer.THREE_HOURLY, "forecast_threehourly.json")
    else:
        met_office.nearest_location_observation(lat, lng)
        met_office.nearest_location_forecast(lat, lng, metoffer.DAILY)
        met_office.nearest_location_forecast(lat, lng, metoffer.THREE_HOURLY)

    # Only to be used to create test data for unit aiml_tests

