Enamel - Porcelain API for OpenStack
====================================

Enamel is a service that exposes user-friendly "porcelain_" REST API commands
for creating related or composed resources in an OpenStack deployment.

.. _porcelain: https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain

Why?
----

There are a number of motivations behind the Enamel project.

We feel OpenStack Nova suffers from a number of problems that are a result of
two characteristics of the `OpenStack Compute API`_:

* The OpenStack Compute API serves as a proxy for non-Compute API resources,
  like images, volumes, and networks
* Evolution of the OpenStack Compute API over time has resulted in some API
  calls that can create singular resource entities as well as multiple resource
  entities of the same or different types

Our aim is to build a new user-friendly set of REST APIs in Enamel and slowly
deprecate parts of the OpenStack Compute API that deal with composed resources
or proxy to non-Compute APIs.

.. _OpenStack Compute API: http://developer.openstack.org/api-ref-compute-v2.1.html

Why not Heat?
~~~~~~~~~~~~~

The astute reader will likely point out that OpenStack already has the Heat_
project that provides a higher-level orchestration API. Why do we not simply
recommend using Heat and the `OpenStack Orchestration API`_ for "porcelain" API
commands to OpenStack?

.. _Heat: https://wiki.openstack.org/wiki/Heat
.. _OpenStack Orchestration API: http://developer.openstack.org/api-ref-orchestration-v1.html

There are a few reasons we chose not to use Heat for this purpose:

* Heat's API is platform-layer-centric
  
  By this we mean that the API's resources (stacks, stack templates,
  software configurations, etc) are all designed around an end-user
  who wishes to describe their virtual machine deployment topology and
  operate on that topology of resources as a unit.

  Enamel's API is plumbing-layer-centric, by which we mean that
  Enamel is concerned with creating user-friendly ways of performing
  multiple low-level, granular steps of a well-known process in a
  controlled fashion.

* Heat's API is declarative

  Porcelain APIs are imperative. They wrap lower-level granular
  plumbing calls in a single user-friendly call.

* Heat's API has stateful objects

  Enamel's only stateful resource object is a Task, which allows the
  user of Enamel's API to receive notification and query for an event
  timeline for the porcelain API command's execution. Enamel does not
  and will not have any concept of saved "macros" in the sense of
  Heat's templates and software configurations.

Architecture
------------

TODO

REST API
--------

Principles
~~~~~~~~~~
