/*
 Highstock JS v10.2.0 (2022-07-05)

 Advanced Highcharts Stock tools

 (c) 2010-2021 Highsoft AS
 Author: Torstein Honsi

 License: www.highcharts.com/license
*/
(function(b){"object"===typeof module&&module.exports?(b["default"]=b,module.exports=b):"function"===typeof define&&define.amd?define("highcharts/modules/full-screen",["highcharts"],function(e){b(e);b.Highcharts=e;return b}):b("undefined"!==typeof Highcharts?Highcharts:void 0)})(function(b){function e(b,c,e,f){b.hasOwnProperty(c)||(b[c]=f.apply(null,e),"function"===typeof CustomEvent&&window.dispatchEvent(new CustomEvent("HighchartsModuleLoaded",{detail:{path:c,module:b[c]}})))}b=b?b._modules:{};
e(b,"Extensions/FullScreen.js",[b["Core/Chart/Chart.js"],b["Core/Globals.js"],b["Core/Renderer/HTML/AST.js"],b["Core/Utilities.js"]],function(b,c,e,f){var g=f.addEvent,h=f.fireEvent;f=function(){function b(a){this.chart=a;this.isOpen=!1;a=a.renderTo;this.browserProps||("function"===typeof a.requestFullscreen?this.browserProps={fullscreenChange:"fullscreenchange",requestFullscreen:"requestFullscreen",exitFullscreen:"exitFullscreen"}:a.mozRequestFullScreen?this.browserProps={fullscreenChange:"mozfullscreenchange",
requestFullscreen:"mozRequestFullScreen",exitFullscreen:"mozCancelFullScreen"}:a.webkitRequestFullScreen?this.browserProps={fullscreenChange:"webkitfullscreenchange",requestFullscreen:"webkitRequestFullScreen",exitFullscreen:"webkitExitFullscreen"}:a.msRequestFullscreen&&(this.browserProps={fullscreenChange:"MSFullscreenChange",requestFullscreen:"msRequestFullscreen",exitFullscreen:"msExitFullscreen"}))}b.prototype.close=function(){var a=this,b=a.chart,d=b.options.chart;h(b,"fullscreenClose",null,
function(){if(a.isOpen&&a.browserProps&&b.container.ownerDocument instanceof Document)b.container.ownerDocument[a.browserProps.exitFullscreen]();a.unbindFullscreenEvent&&(a.unbindFullscreenEvent=a.unbindFullscreenEvent());b.setSize(a.origWidth,a.origHeight,!1);a.origWidth=void 0;a.origHeight=void 0;d.width=a.origWidthOption;d.height=a.origHeightOption;a.origWidthOption=void 0;a.origHeightOption=void 0;a.isOpen=!1;a.setButtonText()})};b.prototype.open=function(){var a=this,b=a.chart,d=b.options.chart;
h(b,"fullscreenOpen",null,function(){d&&(a.origWidthOption=d.width,a.origHeightOption=d.height);a.origWidth=b.chartWidth;a.origHeight=b.chartHeight;if(a.browserProps){var e=g(b.container.ownerDocument,a.browserProps.fullscreenChange,function(){a.isOpen?(a.isOpen=!1,a.close()):(b.setSize(null,null,!1),a.isOpen=!0,a.setButtonText())}),c=g(b,"destroy",e);a.unbindFullscreenEvent=function(){e();c()};var f=b.renderTo[a.browserProps.requestFullscreen]();if(f)f["catch"](function(){alert("Full screen is not supported inside a frame.")})}})};
b.prototype.setButtonText=function(){var a=this.chart,b=a.exportDivElements,d=a.options.exporting,c=d&&d.buttons&&d.buttons.contextButton.menuItems;a=a.options.lang;d&&d.menuItemDefinitions&&a&&a.exitFullscreen&&a.viewFullscreen&&c&&b&&(b=b[c.indexOf("viewFullscreen")])&&e.setElementHTML(b,this.isOpen?a.exitFullscreen:d.menuItemDefinitions.viewFullscreen.text||a.viewFullscreen)};b.prototype.toggle=function(){this.isOpen?this.close():this.open()};return b}();c.Fullscreen=f;g(b,"beforeRender",function(){this.fullscreen=
new c.Fullscreen(this)});"";return c.Fullscreen});e(b,"masters/modules/full-screen.src.js",[],function(){})});
