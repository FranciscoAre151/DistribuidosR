docker run -v /etc/localtime:/etc/localtime:ro -v /home/user1/Documents/P2Distribuidos:/P2Distribuidos --network my_overlay_network --rm -it --name datos datos

docker run --network  my_overlay_network --rm -it --name miembro1 miembro1
docker run --network  my_overlay_network --rm -it  --name miembro1.1 miembro1
docker run --network  my_overlay_network --rm -it  --name miembro2 miembro2
docker run --network  my_overlay_network --rm -it  --name miembro2.1 miembro2
docker run --network  my_overlay_network --rm -it  --name miembro3 miembro3
docker run --network  my_overlay_network --rm -it  --name miembro3.1 miembro3
docker run -v /var/run/docker.sock:/var/run/docker.sock --network my_overlay_network --rm -it  --name servidor -p 6004:6004 servidor
