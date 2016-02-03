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

Enamel has a number of high-level design goals:

* Model sets of related actions into task flows that can be easily understood,
  instrumented, debugged, and extended
* Have stateless worker services that can grab a task flow and execute,
  restart, and prioritize whole or partial task flows

There are two primary components in the Enamel architecture. A set of stateless
HTTP/WSGI services provide a REST API for end users to call and a set of
stateless worker services that execute related actions.

A typical event flow for Enamel looks like the following:

1) User issues call to REST API to perform an action (e.g. POST /servers to
   create one or more server instances)

2) Enamel API service grabs the authentication credentials used in the HTTP
   request and communicates with the Barbican secure key storage service,
   asking it to return a key for the user credentials. If Barbican has the key,
   great. If not, Enamel creates a key for the user credentials. This secure
   key is essential to avoid storing user credentials or passing user
   credentials between components. Since an Enamel task can take a long time to
   execute, we need a method of recreating a Keystone session/token in case an
   initial token expires.

3) Enamel API service creates a Task resource in a backend data store and
   returns the task ID to the caller as a 202 Accepted response. The Task
   resource will contain the Barbican key created in step 2.

4) Enamel API service serializes the Task resource into a message format and
   publishes the message to a topical message queue exchange. The topic for the
   exchange will typically be the type of the Task. This means that deployers
   of Enamel may spin up different numbers of worker processes for different
   types of tasks.

5) Enamel worker services consume Task messages from the topical queues that
   they are listening on. The Task message will contain some information on
   what stage or subtask the Task is currently on, whether or not the stage has
   been restarted or retried, and the executable actions to take for the Task.

6) Upon completing the entire task or a set of subtasks in the task, the worker
   service process writes to a backing data store the time the subtask took.

7) The end user, in the meantime, will be able to poll the API service to
   determine the latest state of the API call.

REST API
--------

`POST /servers`
...............

Creates one or more server instances in an OpenStack cloud.

`GET /tasks`
............

Returns the currently running tasks for the authenticated user.

`GET /tasks/{id}`
.................

Returns details about a specific task.

Principles
~~~~~~~~~~
