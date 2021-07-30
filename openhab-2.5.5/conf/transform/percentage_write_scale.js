// Wrap everything in a function (no global variable pollution)
// variable "input" contains data passed by openHAB
(function(inputData) {
    // on read: the polled number as string
    // on write: openHAB command as string
    var MULTIPLY_BY = 1;
    return Math.round(parseFloat(inputData, 10) * MULTIPLY_BY);
})(input)