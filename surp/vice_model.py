import pandas as pd
import json
import os

from . import vice_utils


class ViceModel():
    """
    A convineince class which holds and works with VICE multioutputs

    Attributes
    ----------
    history: ``pd.DataFrame``
        Contains a data frame
        See vice.output.history
    mdf: ``pd.DataFrame``
        A dataframe of metallicity distribution functions by radius
    stars: ``pd.DataFrame``
    apogee_stars
    unfiltered_stars
    """

    def __init__(self, stars_unsampled, history, mdf, stars=None):
        self.stars_unsampled = pd.DataFrame(stars_unsampled)

        if stars is None:
            stars = vice_utils.create_star_sample(self.stars_unsampled)

        self.stars = pd.DataFrame(stars)

        self.history = pd.DataFrame(history)
        self.mdf = pd.DataFrame(mdf)

    @classmethod
    def from_saved(cls, filename):
        """
        given the filename, 
        """

        with open(filename, "r") as f:
            d = json.load(f)

        keys = ["stars_unsampled", "history", "mdf", "stars"]
        assert all([key in d.keys() for key in keys])

        return cls(*[d[key] for key in keys])

    @classmethod
    def from_vice(cls, filename, zone_width):
        name = os.path.splitext(filename)[0]
        json_name = f"{name}.json"

        output = vice_utils.load_vice(filename, zone_width=zone_width)
        history, mdf = vice_utils.reduce_history(output, zone_width=zone_width)
        stars_unsampled = vice_utils.reduce_stars(output)

        return cls(stars_unsampled, history, mdf)


    def save(self, filename, overwrite=False):
        if os.path.exists(filename) and not overwrite:
            print("not overwritng file")
            return

        d = {
            "stars": self.stars.to_dict(),
            "stars_unsampled": self.stars_unsampled.to_dict(),
            "history": self.history.to_dict(),
            "mdf": self.mdf.to_dict(),
            }

        with open(filename, "w") as f:
            json.dump(d, f)



