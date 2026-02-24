## Observer Pattern

### Overview

A python class that implements an extended observer pattern. Intended as parent class for other classes that need to make use of the observer pattern structure.

### Methods
- register_listener: Allows another class to register a Listener on this class.
- mute_listener: Prevents a Listener from receiving messages of a given event.
- unmute_listener: Allows a Listener to receive messages of the event again.
- destroy_listener: Removes a Listener from the list of registered listeners for a given event.
- mute_event: Prevents all Listeners from receiving messages of a given event.
- unmute_event: Allows all Listeners to receive messages of the event again.
- destroy_event: Removes the event (and thereby all listeners) from the list of events.
- send_whisper: Sends a message to a specific Listener for a given event.
- send_messages: Sends a message to all Listeners for a given event.
