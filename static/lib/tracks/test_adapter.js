// test adapter, JSON


WireIt.WiringEditor.adapters.tracks = {
	
	/**
	 * You can configure this adapter to different schemas.
	 * url can be functions !
	 */
	config: {
		listWirings: {
			method: 'POST',
			url: 'listWirings/'
		},

		saveWiring: {
			method: 'POST',
			url: 'saveWiring/'
		},
		
		runReduction: {
			method: 'POST',
			url: 'runReduction/'
		},
	},
	
	init: function() {
		YAHOO.util.Connect.setDefaultPostHeader('application/json');
	},
	
	listWirings: function(val, callbacks) {
		this._sendRequest("listWirings", val, callbacks);
	},
	
	saveWiring: function(val, callbacks) {
		var wiring = {};
		YAHOO.lang.augmentObject(wiring, val);	
		this._sendRequest("saveWiring", wiring, callbacks);
	},
	
	runReduction: function(val, callbacks) {
		var wiring = {};
		YAHOO.lang.augmentObject(wiring, val);
		this._sendRequest("runReduction", val, callbacks);
	},
	
	
	_sendRequest: function(action, value, callbacks) {
		/*
		var params = [];
		for(var key in value) {
			if(value.hasOwnProperty(key)) {
				// edited 6/22, now stringifies value
				params.push(window.encodeURIComponent(key) +"="+window.encodeURIComponent(value[key]));							
			}
		}
		var postData = params.join('&');
		*/
		var postData = 'data=' + YAHOO.lang.JSON.stringify(value);
		
		var url = "";
		if( YAHOO.lang.isFunction(this.config[action].url) ) {
			url = this.config[action].url(value);
		}
		else {
			url = this.config[action].url;
		}
		var method = "";
		if( YAHOO.lang.isFunction(this.config[action].url) ) {
			method = this.config[action].method(value);
		}
		else {
			method = this.config[action].method;
		}
		YAHOO.util.Connect.asyncRequest(method, url, {
			success: function(o) {
				var s = o.responseText;
				         // CHANGED (7/5/11), JSON parsing was not working
					 //r = YAHOO.lang.JSON.parse(r)
					 r = eval('(function() { return ' + s + '; })()');
			 	callbacks.success.call(callbacks.scope, r);
			},
			failure: function(o) {
				var error = o.status + " " + o.statusText;
				callbacks.failure.call(callbacks.scope, error);
			}
		},postData);
	}
	
};
