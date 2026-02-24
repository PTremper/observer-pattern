"""Module that implements an Observer Pattern/Event Listeners."""

import logging
from collections.abc import Callable
from typing import Any, Unpack

logger = logging.getLogger(__name__)


class ObserverPattern:
    """Parent class that implements an Observer Pattern/Event Listeners.

    This class provides a framework for implementing the Observer Pattern, which allows objects to subscribe
    to events and receive notifications when those events occur.
    The ObserverPattern class maintains a list of registered listeners and dispatches events to them when they occur.

    Methods:
        register_listener: Allows another Class to register a Listener on this Class.
        mute_listener: Prevents a Listener from receiving messages of a given event.
        unmute_listener: Allows a Listener to receive messages of the event again.
        destroy_listener: Removes a Listener from the list of registered listeners for a given event.
        mute_event: Prevents all Listeners from receiving messages of a given event.
        unmute_event: Allows all Listeners to receive messages of the event again.
        destroy_event: Removes the event (and thereby all listeners) from the list of events.
        send_whisper: Sends a message to a specific Listener for a given event.
        send_messages: Sends a message to all Listeners for a given event.

    """

    def __init__(self) -> None:
        """Initialize the ObserverPattern instance."""
        self.__events = []

    def register_listener(
        self,
        event_name: str,
        callback: Callable[..., Any],
        listener_name: str | None = None,
        *,
        force_listener_overwrite: bool = False,
        **kwargs: Unpack[dict[str, Any]],
    ) -> None:
        """Allows another Class to register a Listener on this Class.

        Arguments:
            event_name: String, Name of dispatched Event to listen to
            callback: Function Object, Whatever is to be executed when catching the Event.
                Important: callback needs to have allow argument 'payload' even if it isn't processed in the function.
            listener_name: String, Name of the Listener to avoid duplicates and allow destruction. Default: None
            force_listener_overwrite: Bool, Overwrite Listener with same Name if it exists. Default: False
            **kwargs: any, arguments to be handed over to the Callback

        """
        # create listener
        listener = {
            "listener_name": listener_name,
            "__mute__": False,
            "callback": callback,
            "kwargs": kwargs,
        }

        # check event existence and create if it does not exist
        evt = next((item for item in self.__events if event_name in item), None)
        if evt is None:  # event does not exist yet -> append the new event
            self.__events.append({event_name: [listener]})
        elif listener_name is None:  # event exists: no listener name given to register for event
            evt[event_name].append(listener)  # append anonymous listener
        # event exists, check to register new listener. listener name is given.
        else:
            lst = next((item for item in evt[event_name] if item["listener_name"] == listener_name), None)
            if lst is None:  # listener name does not exist yet
                evt[event_name].append(listener)  # append named listener
            else:  # listener with that name exists
                logger.warning(f"Listener with name {listener_name} already exists on event {event_name}.")
                if force_listener_overwrite:
                    logger.warning(f"Overwriting Listener {listener_name}.")
                    evt[event_name].remove(lst)
                    evt[event_name].append(listener)
                else:
                    logger.warning("Rejecting new Listener.")

    def mute_listener(self, event_name: str, listener_name: str) -> None:
        """Allows to mute a listener so it does not receive messages."""
        for evt in self.__events:
            if event_name in evt:
                for lst in evt[event_name]:
                    if lst["listener_name"] == listener_name:
                        lst["__mute__"] = True

    def unmute_listener(self, event_name: str, listener_name: str) -> None:
        """Allows to unmute a listener so it does receive messages again."""
        for evt in self.__events:
            if event_name in evt:
                for lst in evt[event_name]:
                    if lst["listener_name"] == listener_name:
                        lst["__mute__"] = False

    def destroy_listener(self, event_name: str, listener_name: str) -> None:
        """Destroy a listener."""
        for evt in self.__events:
            if event_name in evt:
                lst = next((item for item in evt[event_name] if item["listener_name"] == listener_name), None)
                if lst is not None:
                    evt[event_name].remove(lst)

    def mute_event(self, event_name: str) -> None:
        """Mute an event so it does not dispatch messages even when triggered."""
        for evt in self.__events:
            if event_name in evt:
                for lst in evt[event_name]:
                    lst["__mute__"] = True

    def unmute_event(self, event_name: str) -> None:
        """Umute an event so it does dispatch messages again when triggered."""
        for evt in self.__events:
            if event_name in evt:
                for lst in evt[event_name]:
                    lst["__mute__"] = False

    def destroy_event(self, event_name: str) -> None:
        """Destroy an event. Removes the event from the list of events that trigger messages."""
        evt = next((item for item in self.__events if event_name in item), None)
        if evt is not None:
            self.__events.remove(evt)

    # only one specific listener, optional payload as first kwarg
    def send_whisper(self, event_name: str, listener_name: str, payload: Any | None = None) -> None:  # noqa: ANN401
        """Send a message only to target listener."""
        logger.debug(f"Event {event_name} called as a Whisper.")

        # check event existence and dispatch messsages
        evt = next((item for item in self.__events if event_name in item), None)
        if evt is not None:
            lst = next((item for item in evt[event_name] if item["listener_name"] == listener_name), None)
            if lst is None:
                logger.warning(f"Listener {listener_name} does not exist for event {event_name}. Cannot send whisper.")
            elif not lst["__mute__"]:
                logger.debug(f"Calling callback as {lst['callback'].__name__}.")
                lst["callback"](payload=payload, **lst["kwargs"])
            else:
                logger.warning(f"Listener {listener_name} is muted. Event {event_name} was not received.")

    # sends optional payload as first kwarg
    def send_messages(self, event_name: str, payload: Any | None = None) -> None:  # noqa: ANN401
        """Send message for a given event, notifying all listeners."""
        logger.debug(f"Event {event_name} called.")

        # check event existence and dispatch messsages
        evt = next((item for item in self.__events if event_name in item), None)
        if evt is not None:
            for lst in evt[event_name]:
                if not lst["__mute__"]:
                    logger.debug(f"Calling callback as {lst['callback'].__name__}.")
                    lst["callback"](payload=payload, **lst["kwargs"])


# testing


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),  # Output to stdout
        ],
    )
    # example test

    # class inheriting the pattern
    class Sender(ObserverPattern):
        """Sender class as child class of the observer pattern."""

    class Receiver:
        """Receiver class, which can register a listeners on a sender instance."""

        def __init__(self) -> None:
            """Initialize the receiver class."""

        # register listener on sender instance with event name, listener name and callback function c0
        # the callback function uses kwargs and prints them
        def register_at_sender(
            self,
            sender_instance: Sender,
            event_name: str,
            listener_name: str,
            **kwargs: Unpack[dict[str, Any]],
        ) -> None:
            """Register a listener on the sender instance."""
            sender_instance.register_listener(
                event_name=event_name,
                listener_name=listener_name,
                callback=self.c0,
                kwargs=kwargs,
            )
            print(f"appending listener for event: {event_name=}.")

        def c0(
            self,
            payload: str | int | None = None,
            **kwargs: Unpack[dict[str, Any]],
        ) -> None:
            """Callback function c0."""
            print("c0 Callback triggered")
            print(f"{kwargs}")
            if payload is not None:
                print(f"Received payload: {payload}")

    # -----------------------------------------------------------------

    s0 = Sender()
    r0 = Receiver()

    r0.register_at_sender(
        sender_instance=s0,
        event_name="event1",
        listener_name="listener1",
        kwarg1="This is kwarg1",
        kwarg2="This is kwarg2",
    )

    s0.send_messages(event_name="event1", payload=21)
