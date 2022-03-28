import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

DEFAULT_EXCLUDE = '.js,googleads,facebook,youtube,chartbeat,.jpg,.ico,.css,bing.com,fonts,twitter,google.com,' \
                  'google.co.uk,.svg,appdynamics.com,.gif,.png,.omtrdc.net,demdex.net,cm.everesttech.net,' \
                  'fundslibrary.co.uk,t.co,www.googletagmanager.com,ytimg.com,ajax/menus,lightstreamer,' \
                  'loginstatus,cms_services.php'
