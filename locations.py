class Location():
    def __init__(self,data):
        self.data = data

    def is_mgrs(self):
        """
        @brief checks if location data is MGRS
        @params None
        """
        if isinstance(self.data,list):
            return False
        else:
            pass

    def is_latlon(self):
        """
        @brief checks if location data is Lat,Lon
        @params None
        """
        pass

    def is_utm(self):
        """
        @brief checks if location data is UTM
        @params None
        """
        if isinstance(self.data,list):
            return False
        else:
            pass

    def is_ne(self):
        """
        @brief checks if location data is Northing,Easting
        @params None
        """
        pass



    def as_mgrs(self):
        """
        @brief converts location data to MGRS
        @params None
        """
        if self.is_mgrs():
            return self.data
        else:
            pass

    def as_latlon(self):
        """
        @brief converts location data to Lat,Lon
        @params None
        """
        if self.is_latlon():
            return self.data
        else:
            pass

    def as_utm(self):
        """
        @brief converts location data to UTM (similar to MGRS but not quite)
        @params None
        """
        if self.is_utm():
            return self.data
        else:
            pass
    def as_ne(self):
        """
        @brief converts location data to Northing,Easting
        @params None
        """
        if self.is_ne():
            return self.data
        else:
            pass

    def as_address(self):
        """
        @brief geocodes to plaintext address
        @params None
        """
        d = None
        if not self.is_latlon():
            d = self.as_latlon()
        else:
            d = self.data

        # geocode d
        print(d)
