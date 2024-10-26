## Generating Python Code from the `.proto` File

To generate the Python gRPC code from the `nobel_prize.proto` file, run the following command in terminal:

```bash
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. nobel_prize.proto

