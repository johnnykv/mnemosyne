*************
Normalization
*************


Dataflow
========

.. digraph:: foo


      compound=true;

      subgraph cluster_1 {
         style=filled;
         fillcolor="cornsilk2"
         node [style=filled];
         feedpuller [label="Feedpuller"];
         normalizer [label="Normalizer"];
         webapi [label="WebAPI"];
         label = "Mnemosyne";
      }

      subgraph cluster_2 {
         node [shape=box]
         style=filled;
         fillcolor=".7 .3 1.0";
         node [style=filled];
         hpfeed [label="HPFeeds"];
         file [label="Files"]
         url [label="URLs"]
         session [label="Sessions"]
         label = "Mongo collections";
         labelloc = b;
      }


      hpf [label="hpfeeds.honeycloud.net"];
      hpf -> feedpuller [color=red];
      feedpuller -> hpfeed [color=red];
      hpfeed -> normalizer [color=red];
      normalizer -> file [color=green];
      normalizer -> url [color=green];
      normalizer -> session [color=green];


      session -> webapi [ ltail=cluster_2, lhead=cluster_1];


Overview
============

Some text on extractions, attachments and entities here - the big picture.

.. digraph:: foo


   node [fontsize = "10", shape = "box", style="filled", fillcolor="aquamarine"];

   rankdir=LR;
   "HPFeed" -> "Session"
   "HPFeed" -> "URL"
   "HPFeed" -> "File"

   node [fontsize = "7", shape = "circle", style="filled", fillcolor="aquamarine"];
   "Session" -> "protocol"


Mongo collections
=================
General information on collections here, also a bit about the schemaless database.

HPFeed
------
Detailed description of the HPFeeds entity.

Session
-------
Detailed description of the Session entity.

URL
---
Detailed description of the URL entity.

File
----
Detailed description of the File entity.

Mongo queries
=============
Some interesting examples on mongo queries in relation to HP.