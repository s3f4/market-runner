class Util:

    @staticmethod
    def isfloat(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def get_api_params():
        import json
        with open("api.json") as f:
            data = json.load(f)
        return data
