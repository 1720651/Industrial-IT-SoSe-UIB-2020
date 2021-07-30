// Wrap everything in a function (no global variable pollution)
// variable "input" contains data passed by openHAB
(function(inputData) {
    // on read: the polled number as string
    // on write: openHAB command as string
    var DIVIDE_BY = 100;
    return parseFloat(inputData) / DIVIDE_BY;
})(input)