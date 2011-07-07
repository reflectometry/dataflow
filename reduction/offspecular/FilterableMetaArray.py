from MetaArray import MetaArray
from numpy import ndarray
import copy

class FilterableMetaArray(MetaArray):
    def __new__(*args, **kwargs):
        subarr = MetaArray.__new__(*args, **kwargs)
        # causing problems with parsing
        #subarr.extrainfo = subarr._info[-1]
        return subarr
    
    def filter(self, filtername, *args, **kwargs):
        import filters
        return filters.__getattribute__(filtername)().apply(self, *args, **kwargs)
        #return filters.__getattribute__(filtername)(*args, **kwargs).apply(self)

    
    def __deepcopy__(self, memo):
        return FilterableMetaArray(self.view(ndarray).copy(), info=self.infoCopy())

