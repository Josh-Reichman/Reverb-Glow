from kivy.app import App
from kivy.properties import NumericProperty, AliasProperty, BooleanProperty
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from math import fabs
import platform
import pigpio
import lampi_util


# kludgey waht to figure out if we're on the Raspberry Pi
if 'arm' not in platform.platform():
    class LampDriver(object):
        def set_lamp_state(self, hue, saturation, brightness, is_on):
            pass

else:
    from lamp_driver import LampDriver

TOLERANCE = 0.000001


class ReverbApp(App):
    _hue = NumericProperty(1.0)
    _saturation = NumericProperty(1.0)
    _brightness = NumericProperty(1.0)
    lamp_is_on = BooleanProperty(True)

    def _get_hue(self):
        return self._hue

    def _set_hue(self, value):
        if fabs(self.hue - value) > TOLERANCE:
            self._hue = value

    def _get_saturation(self):
        return self._saturation

    def _set_saturation(self, value):
        if fabs(self.saturation - value) > TOLERANCE:
            self._saturation = value

    def _get_brightness(self):
        return self._brightness

    def _set_brightness(self, value):
        if fabs(self.brightness - value) > TOLERANCE:
            self._brightness = value

    hue = AliasProperty(_get_hue, _set_hue, bind=['_hue'])
    saturation = AliasProperty(_get_saturation, _set_saturation,bind=['_saturation'])
    brightness = AliasProperty(_get_brightness, _set_brightness,bind=['_brightness'])
    gpio17_pressed = BooleanProperty(False) #right button
    gpio22_pressed = BooleanProperty(False) #2nd right button
    gpio23_pressed = BooleanProperty(False) #2nd left button
    gpio27_pressed = BooleanProperty(False) #left button



    def on_start(self):
        self.lamp_driver = LampDriver()
        Clock.schedule_once(lambda dt: self._update_leds(), 0.01)
        self.set_up_GPIO_and_IP_popup()

    def on_hue(self, instance, value):
        Clock.schedule_once(lambda dt: self._update_leds(), 0.01)

    def on_saturation(self, instance, value):
        Clock.schedule_once(lambda dt: self._update_leds(), 0.01)

    def on_brightness(self, instance, value):
        Clock.schedule_once(lambda dt: self._update_leds(), 0.01)

    def on_lamp_is_on(self, instance, value):
        Clock.schedule_once(lambda dt: self._update_leds(), 0.01)

    def _update_leds(self):
        self.lamp_driver.set_lamp_state(self._hue, self._saturation,
                                        self._brightness, self.lamp_is_on)

    def set_up_GPIO_and_IP_popup(self):
        self.pi = pigpio.pi()
        self.pi.set_mode(17, pigpio.INPUT)
        self.pi.set_mode(22, pigpio.INPUT)
        self.pi.set_mode(23, pigpio.INPUT)
        self.pi.set_mode(27, pigpio.INPUT)
        self.pi.set_pull_up_down(17, pigpio.PUD_UP)
        self.pi.set_pull_up_down(22, pigpio.PUD_UP)
        self.pi.set_pull_up_down(23, pigpio.PUD_UP)
        self.pi.set_pull_up_down(27, pigpio.PUD_UP)

        Clock.schedule_interval(self._poll_GPIO, 0.05)
        self.popup = Popup(title='IP Addresses',
                           content=Label(text='IP ADDRESS WILL GO HERE'),
                           size_hint=(1, 1), auto_dismiss=False)
        self.popup.bind(on_open=self.update_popup_ip_address)

    def update_popup_ip_address(self, instance):
        interface = "wlan0"
        ipaddr = lampi_util.get_ip_address(interface)
        instance.content.text = "{}: {}".format(interface, ipaddr)

    def on_gpio17_pressed(self, instance, value):
        if value:
            self.popup.open()
        else:
            self.popup.dismiss()

    def on_gpio22_pressed(self, instance, value):
        if value:
            self.popup.open()
        else:
            self.popup.dismiss()

    def on_gpio23_pressed(self, instance, value):
        if value:
            self.popup.open()
        else:
            self.popup.dismiss()

    def on_gpio27_pressed(self, instance, value):
        if value:
            self.popup.open()
        else:
            self.popup.dismiss()

    def _poll_GPIO(self, dt):
        self.gpio17_pressed = not self.pi.read(17)
        self.gpio22_pressed = not self.pi.read(22)
        self.gpio23_pressed = not self.pi.read(23)
        self.gpio27_pressed = not self.pi.read(27)
