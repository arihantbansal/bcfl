import socket
import threading
import argparse
import logging


format = "%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s: %(message)s"


def handle(buffer, direction, src_address, src_port, dst_address, dst_port):
  """
  intercept the data flows between local port and the target port
  """
  if direction:
    print(
        f"{src_address, src_port} -> {dst_address, dst_port} {len(buffer)} bytes"
    )
  else:
    print(
        f"{src_address, src_port} <- {dst_address, dst_port} {len(buffer)} bytes"
    )
  print(buffer)
  return buffer


def transfer(src, dst, direction):
  src_address, src_port = src.getsockname()
  dst_address, dst_port = dst.getsockname()
  while True:
    try:
      buffer = src.recv(4096*16)
      if len(buffer) > 0:
        dst.send(
            handle(
                buffer, direction, src_address, src_port, dst_address, dst_port
            )
        )
    except Exception as e:
      print(repr(e))
      break
  print(f"Closing connect {src_address, src_port}! ")
  src.close()
  print(f"Closing connect {dst_address, dst_port}! ")
  dst.close()


def server(local_host, local_port, remote_host, remote_port):
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  server_socket.bind((local_host, local_port))
  server_socket.listen(0x40)
  print(f"Server started {local_host, local_port}")
  print(
      f"Connect to {local_host, local_port} to get the content of {remote_host, remote_port}"
  )
  while True:
    src_socket, src_address = server_socket.accept()
    print(
        f"[Establishing] {src_address} -> {local_host, local_port} -> ? -> {remote_host, remote_port}"
    )
    try:
      dst_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      dst_socket.connect((remote_host, remote_port))
      print(
          f"[OK] {src_address} -> {local_host, local_port} -> {dst_socket.getsockname()} -> {remote_host, remote_port}"
      )
      s = threading.Thread(target=transfer, args=(
          dst_socket, src_socket, False))
      r = threading.Thread(target=transfer, args=(
          src_socket, dst_socket, True))
      s.start()
      r.start()
    except Exception as e:
      print(repr(e))


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      "--listen-host", help="the host to listen", required=True)
  parser.add_argument(
      "--listen-port", type=int, help="the port to bind", required=True
  )
  parser.add_argument(
      "--connect-host", help="the target host to connect", required=True
  )
  parser.add_argument(
      "--connect-port", type=int, help="the target port to connect", required=True
  )
  args = parser.parse_args()
  server(args.listen_host, args.listen_port,
         args.connect_host, args.connect_port)


if __name__ == "__main__":
  main()
