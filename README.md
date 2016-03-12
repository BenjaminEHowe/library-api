# library-api #

An API to talk to libraries developed at Brumhack 4.0. We're planning to support SirsiDynix Enterprise and WebPAC PRO - support for other library software will be added  as requested.

# Specification #

_This specification should not be considered final - please feel free to make suggestions._

## Library object ##

This represents a physical library. It's actually provided by different classes depending on the software which the library uses.

**\__init(url)__** - create the object by passing the url for the library catalogue (e.g. <https://rdg.ent.sirsidynix.net.uk/client/en_GB/main>, <https://library.aston.ac.uk/>). Magic will figure out what software the library is running and load appropriate functions into the library class.

Provides functions like:
* **login(userid, password)** - accepts login credentials, returns a borrower object.
* **search(query=None, title=None, author=None, ean=None)** - performs a search, returning a (potentially empty) list of items. Optionally, search only within the title and / or author attributes.
* **get_item(id)** - gets an item, where the id is an EAN (ISBN-13) or implementation-specific id.

Also, provides functions for the borrower object (see below).

### search data structure ###

A dictionary with the following keys:

* A string containing the EAN / ISBN-13 (or an implementation specific id - something that makes it possible to use get_item for more information).
* A string containing the title.
* A string containing the name(s) of the author(s) / artist(s) / key actor(s).
* A string containing the type of item in lower case, for example, book, periodical, dvd, cd, bluray, etc. This list is not intended to be complete.

## Borrower object ##

This represents a borrower. It must be tied to a library, otherwise we don't know how to log in! It's basically a wrapper to allow authenticated requests without having to constantly pass an authenticated session - all the functions are actually provided by the classes for libraries.

**\__init__(userid, password, library)** - create the object by passing the userid and password to log in with, and the library to log into. **You shouldn't create a borrower directly**, instead call library.login.

Provides functions like:
* **list_items()** - returns a list of items the borrower has.
* **list_reservations()** - returns a list of reservations the borrower has placed.
* **renew(id)** - accpets an EAN (ISBN-13) or implementation-specific ID, returns true if the item was successfully renewed, returns false otherwise.
* **renew_all()** - renews all the items a borrower has.

### list_items data structure ###

A dictionary with the following keys:

* A string containing the EAN / ISBN-13.
* A string containing an ID for the specific copy that the borrower has.
* A [date object](https://docs.python.org/3/library/datetime.html#datetime.date) containing the due date.
* An integer containing the nubmer of times

### list_reservations data structure ###

A dictionary with the following keys:

* A string containing the EAN / ISBN-13.
* An integer containing your position in the queue (with zero meaning the item is available for collection).

## Item data structure ##

This refers to an item. While the item is held by a library as-per the copies (and hance library specific), other similar items migth be available from other libraries. _optional_ values might return NoneType if the data isn't available.

* **author** - a list of strings containing the name(s) of the author(s) / artist(s) / key actor(s).
* **call_number** - the call number where the book can be found.
* **copies** - the number of copies the library owns.
* **copies_available** - the number of copies available.
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
* **type** - the type of item in lower case, for example, book, ebook, periodical, dvd, cd, bluray, etc. This list is not intended to be complete.
* **url** _(optional)_ - the URL associated with the item.
* **volume** _(optional)_ - the volume of the publication.
