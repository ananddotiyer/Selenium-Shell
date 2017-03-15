/*
 * Returns all border properties of the specified element as String,
 * in order of "width style color" delimited by ';' (semicolon) in the form of:
 * 
 * "2px inset #000000;2px inset #000000;2px inset #000000;2px inset #000000"
 * "medium none #ccc;medium none #ccc;1px solid #e5e5e5;medium none #ccc"
 * etc.
 */
var elem = arguments[0]; 
if (elem.currentStyle) {
    // Branch for IE 6,7,8. No idea how this works on IE9, but the script
    // should take care of it.
    var style = elem.currentStyle;
    var border = style['borderTopWidth']
            + ' ' + style['borderTopStyle']
            + ' ' + style['borderTopColor']
            + ';' + style['borderRightWidth']
            + ' ' + style['borderRightStyle']
            + ' ' + style['borderRightColor']
            + ';' + style['borderBottomWidth']
            + ' ' + style['borderBottomStyle']
            + ' ' + style['borderBottomColor']
            + ';' + style['borderLeftWidth']
            + ' ' + style['borderLeftStyle']
            + ' ' + style['borderLeftColor'];
} else if (window.getComputedStyle) {
    // Branch for FF, Chrome, Opera
    var style = document.defaultView.getComputedStyle(elem);
    var border = style.getPropertyValue('border-top-width')
            + ' ' + style.getPropertyValue('border-top-style')
            + ' ' + style.getPropertyValue('border-top-color')
            + ';' + style.getPropertyValue('border-right-width')
            + ' ' + style.getPropertyValue('border-right-style')
            + ' ' + style.getPropertyValue('border-right-color')
            + ';' + style.getPropertyValue('border-bottom-width')
            + ' ' + style.getPropertyValue('border-bottom-style')
            + ' ' + style.getPropertyValue('border-bottom-color')
            + ';' + style.getPropertyValue('border-left-width')
            + ' ' + style.getPropertyValue('border-left-style')
            + ' ' + style.getPropertyValue('border-left-color');
}
// highlight the element
elem.style.border = '2px solid red';
return border;