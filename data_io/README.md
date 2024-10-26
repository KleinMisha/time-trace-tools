```mermaid
flowchart TD;
    A[Start] --> B[Process 1];
    B --> C[Process 2];
    C --> D[End];


sequenceDiagram;
    participant Client
    participant Server
    Client->>Server: Register user
    activate Server
    Server-->>Client: User already exists.
    deactivate Server
```





# modules for reading/writing data 
Contains
----
* raw_mt.py
    * Load raw data from magnetic-tweezers 
    * includes 'legacy mode' to load LabView related data 
* processed.py
    * readers and writers for processed data 
* magnet_script.py
    * load controlling script 
    * can be used to create a set of sections in the time traces corresponding to the magnets performing specific operations 