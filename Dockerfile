FROM docker.elastic.co/elasticsearch/elasticsearch:8.9.0

USER root
RUN chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/data
USER elasticsearch

# single-node + open network + no security
ENV discovery.type=single-node
ENV network.host=0.0.0.0

ENV xpack.security.enabled=false
ENV xpack.security.http.ssl.enabled=false

EXPOSE 9200 9300
