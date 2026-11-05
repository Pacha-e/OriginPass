# Nest application

Validate request bodies on the backend before using their values in domain operations. A Nest input validator can check the fields needed by the operation; browser checks alone can be bypassed ([Nest source](../../../../knowledge/books/T07-book-nest.md), lines 180–189). Inspect the controller's path from request body to validation and service call, and test invalid and oversized inputs ([global rules](../../../../rules/global-rules.md), lines 137–142).
