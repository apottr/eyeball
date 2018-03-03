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
            if self.data[3].isalpha() and not ("," in self.data):
                return True

    def is_latlon(self):
        """
        @brief checks if location data is Lat,Lon
        @params None
        """
        if isinstance(self.data,list):
            if isinstance(self.data[0],int):
                x = str(self.data[0])
            else:
                x = self.data[0]

            if "." in x:
                return True
        else:
            if "," in self.data:
                y = self.data.split(",")
                if "." in y[0]:
                    return True
                else:
                    return False
            else:
                return False
                

    def is_utm(self):
        """
        @brief checks if location data is UTM
        @params None
        """
        if isinstance(self.data,list):
            return False
        else:
            if self.data[3].isalpha() and ("," in self.data):
                return True
    def as_mgrs(self):
        """
        @brief converts location data to MGRS
        @params None
        """
        if self.is_mgrs():
            return self.data
        else:
            if self.is_utm():
                return self.data.replace(","," ")
            elif self.is_latlon():
                #convert latlon to MGRS
                pass

    def as_latlon(self):
        """
        @brief converts location data to Lat,Lon
        @params None
        """
        if self.is_latlon():
            return self.data
        else:
            if self.is_utm():
                #convert utm to latlon
                pass
            elif self.is_mgrs():
                #convert mgrs to latlon
                pass

    def as_utm(self):
        """
        @brief converts location data to UTM (similar to MGRS but not quite)
        @params None
        """
        if self.is_utm():
            return self.data
        else:
            if self.is_mgrs():
                return self.data.replace("")

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


if __name__ == "__main__":
    pass