"use strict";
var RequestData = (function () {
    function RequestData() {
    }
    RequestData.parseFromObject = function (data) {
        for (var _i = 0, _a = RequestData.fields; _i < _a.length; _i++) {
            var field = _a[_i];
            if (!data[field]) {
                throw "Error. required field " + field + " not set";
            }
        }
        var requestData = new RequestData();
        for (var _b = 0, _c = RequestData.fields; _b < _c.length; _b++) {
            var field = _c[_b];
            requestData[field] = data[field];
        }
        return requestData;
    };
    RequestData.fields = ['text', 'username', 'display_name'];
    return RequestData;
}());
exports.RequestData = RequestData;
