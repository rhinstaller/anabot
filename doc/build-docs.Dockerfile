FROM registry.fedoraproject.org/fedora:latest
RUN dnf -y update && dnf -y install make python3-sphinx && dnf clean all
