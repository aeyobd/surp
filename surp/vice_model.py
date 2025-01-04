import pandas as pd
import json
import os

from . import vice_utils
from ._globals import N_SUBGIANTS


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
    unfiltered_stars
    """

    def __init__(self, stars_unsampled, history, mdf, zone_width, 
                 stars=None, seed=-1, num_stars=N_SUBGIANTS, cdf=None):
        """
        Parameters
        ----------
        stars_unsampled: ``pd.DataFrame``
            A dataframe of stars
        history: ``pd.DataFrame``
            A dataframe of history
        mdf: ``pd.DataFrame``
            A dataframe of metallicity distribution functions by radius
        zone_width: ``float``
            The width of the zone
        stars: ``pd.DataFrame``
            A dataframe of stars (weighted samples...)
        num_stars: ``int``
            The number of stars to sample
        cdf: ``pd.DataFrame``
            The cumulative distribution function of the stars. Should contain
            two columns: `R` for Radius and `cdf` for the normalized CDF.
        seed: ``int``
            The seed for the random number generator if need to sample stars.
        """
        self.stars_unsampled = pd.DataFrame(stars_unsampled)

        if stars is None:
            stars = vice_utils.create_star_sample(self.stars_unsampled,
                zone_width=zone_width,
                seed=seed, num=num_stars, cdf=cdf,
            )

        self.zone_width = zone_width
        self.stars = pd.DataFrame(stars)

        self.history = pd.DataFrame(history)
        self.mdf = pd.DataFrame(mdf)

    @classmethod
    def from_file(cls, filename):
        """
        Load a ViceModel from a json file (ideally created by ViceModel.save)
        """

        with open(filename, "r") as f:
            d = json.load(f)

        keys = ["stars_unsampled", "history", "mdf", "stars"]
        assert all([key in d.keys() for key in keys])

        return cls(d["stars_unsampled"], d["history"], d["mdf"], zone_width=None, stars=d["stars"])


    @classmethod
    def from_vice(cls, filename, zone_width,
                  weight_function=vice_utils.ssp_weight,
                  migration_data=None,
                  **kwargs):
        """
        Load a ViceModel from a VICE output file
    
        Parameters
        ----------
        filename: ``str``
            The filename of the VICE output
        zone_width: ``float``
            The width of the zones in the simulations
        weight_function: ``callable``
            A function which takes mass, metallicity, and age of a SSP and returns a weight
        migration_data: ``sting``
            Optional. The extra migration data type if present. 
        **kwargs: ``dict``
            Additional keyword arguments to pass to the class constructor.
        """
        name = os.path.splitext(filename)[0]
        json_name = f"{name}.json"

        output = vice_utils.load_vice(filename, 
            zone_width=zone_width, migration_data=migration_data
            )
        history, mdf = vice_utils.reduce_history(output, zone_width=zone_width)
        stars_unsampled = vice_utils.reduce_stars(output, 
            weight_function=weight_function)

        return cls(stars_unsampled, history, mdf, zone_width, **kwargs)


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



