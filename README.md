# library-api #

An API to talk to libraries developed at Brumhack 4.0. We're planning to support SirsiDynix Enterprise and WebPAC PRO - support for other library software will be added  as requested.

# Specification #

_This specification should not be considered final - please feel free to make suggestions._

## library object ##

This represents a physical library. It's actually provided by different classes depending on the software which the library uses.

**\__init(url)__** - create the object by passing the url for the library catalogue (e.g. <https://rdg.ent.sirsidynix.net.uk/client/en_GB/main>, <https://library.aston.ac.uk/>). Magic will figure out what software the library is running and load appropriate functions into the library class. This should also create the variable `self.authenticated`, and set it to `False`.

Provides functions like:
* **login(userid, password)** - accepts login credentials. On success `self.authenticated` is set to `True`, and `True` is returned.
* **search(query=None, title=None, author=None, ean=None)** - performs a search, returning a (potentially empty) list of items. Optionally, search only within the title, author, or ean attributes.
* **get_item(id)** - gets an item, where the id is an EAN (ISBN-13) or implementation-specific id.

Once authenticated using `login`, the following functions can also be used (attempting to use them without authenticating - i.e. when `not self.authenticated` - will raise `NotAuthenticatedError`:
* **list_items()** - returns a list of items the borrower has.
* **list_reservations()** - returns a list of reservations the borrower has placed.
* **renew(id)** - accpets an EAN (ISBN-13) or implementation-specific ID, returns true if the item was successfully renewed, returns false otherwise.
* **renew_all()** - renews all the items a borrower has.

### `search` data structure ###

A dictionary with the following keys:

* A string containing the EAN / ISBN-13 (or an implementation specific id - something that makes it possible to use get_item for more information).
* A string containing the title.
* A list of strings containing the name(s) of the author(s) / artist(s) / key actor(s).
* A string containing the type of item in lower case (one of: academic_paper, audio, book, ebook, ejournal, electronic, journal, map, other, score, video).

### `list_items` data structure ###

A dictionary with the following keys:

* A string containing the EAN / ISBN-13.
* A string containing an ID for the specific copy that the borrower has.
* A [date object](https://docs.python.org/3/library/datetime.html#datetime.date) containing the due date.
* An integer containing the nubmer of times

### `list_reservations` data structure ###

A dictionary with the following keys:

* A string containing the EAN / ISBN-13.
* An integer containing your position in the queue (with zero meaning the item is available for collection).

## Item data structure ##

This refers to an item. While the item is held by a library as-per the copies (and hance library specific), other similar items migth be available from other libraries. _optional_ values might return `NoneType` if the data isn't available.

A dictionary with the following keys:

* **author** - a list of strings containing the name(s) of the author(s) / artist(s) / key actor(s).
* **call_number** - the call number where the book can be found.
* **copies** - a list of dictionaries with the following keys:
  * **location** - the location (building and call number) where the copy is stored.
  * **type** - an implementation specific string representing the type of loan.
  * **available** - `True` if the copy of the item is available. `False` otherwise.
  * **due** - only populated if `available` is `False`. The date that the book is due back (as a [date object](https://docs.python.org/3/library/datetime.html#datetime.date)).
* **copies_available** - the number of copies available.
* **copies_total** - the number of copies the library owns.
* **date_of_publication** - a [date object](https://docs.python.org/3/library/datetime.html#datetime.date) containing the date of publication - the year must be accurate but the other parts are optional.
* **ean** - the EAN (or ISBN, if you prefer).
* **edition** _(optional)_ - the edition of the publication (integer - so 1 not 1st).
* **issue** _(optional)_ - the issue of the publication.
* **notes** _(optional)_ - any other notes).
* **place_of_publication** _(optional)_ - the place of publication.
* **publisher** - the name of the publisher / label / studio.
* **reservations** _(optional)_ - the number of unfufilled reservations.
* **summary** _(optional)_ - the summary, such as the abstract or blurb.
* **title** - the title of the item.
* **type** - the type of item in lower case (one of: academic_paper, audio, book, ebook, ejournal, electronic, journal, map, other, score, video).
* **url** _(optional)_ - the URL associated with the item.
* **volume** _(optional)_ - the volume of the publication.
