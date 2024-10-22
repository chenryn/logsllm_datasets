var File_Prod_proto protoreflect.FileDescriptor
var file_Prod_proto_rawDesc = []byte{
	0x0a, 0x0a, 0x50, 0x72, 0x6f, 0x64, 0x2e, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x12, 0x08, 0x73, 0x65,
	0x72, 0x76, 0x69, 0x63, 0x65, 0x73, 0x22, 0x26, 0x0a, 0x0b, 0x50, 0x72, 0x6f, 0x64, 0x52, 0x65,
	0x71, 0x75, 0x65, 0x73, 0x74, 0x12, 0x17, 0x0a, 0x07, 0x70, 0x72, 0x6f, 0x64, 0x5f, 0x69, 0x64,
	0x18, 0x01, 0x20, 0x01, 0x28, 0x05, 0x52, 0x06, 0x70, 0x72, 0x6f, 0x64, 0x49, 0x64, 0x22, 0x2d,
	0x0a, 0x0c, 0x50, 0x72, 0x6f, 0x64, 0x52, 0x65, 0x73, 0x70, 0x6f, 0x6e, 0x73, 0x65, 0x12, 0x1d,
	0x0a, 0x0a, 0x70, 0x72, 0x6f, 0x64, 0x5f, 0x73, 0x74, 0x6f, 0x63, 0x6b, 0x18, 0x01, 0x20, 0x01,
	0x28, 0x05, 0x52, 0x09, 0x70, 0x72, 0x6f, 0x64, 0x53, 0x74, 0x6f, 0x63, 0x6b, 0x32, 0x52, 0x0a,
	0x0e, 0x50, 0x72, 0x6f, 0x64, 0x75, 0x63, 0x74, 0x53, 0x65, 0x72, 0x76, 0x69, 0x63, 0x65, 0x12,
	0x40, 0x0a, 0x0f, 0x47, 0x65, 0x74, 0x50, 0x72, 0x6f, 0x64, 0x75, 0x63, 0x74, 0x53, 0x74, 0x6f,
	0x63, 0x6b, 0x12, 0x15, 0x2e, 0x73, 0x65, 0x72, 0x76, 0x69, 0x63, 0x65, 0x73, 0x2e, 0x50, 0x72,
	0x6f, 0x64, 0x52, 0x65, 0x71, 0x75, 0x65, 0x73, 0x74, 0x1a, 0x16, 0x2e, 0x73, 0x65, 0x72, 0x76,
	0x69, 0x63, 0x65, 0x73, 0x2e, 0x50, 0x72, 0x6f, 0x64, 0x52, 0x65, 0x73, 0x70, 0x6f, 0x6e, 0x73,
	0x65, 0x62, 0x06, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x33,
}
var (
	file_Prod_proto_rawDescOnce sync.Once
	file_Prod_proto_rawDescData = file_Prod_proto_rawDesc
)
func file_Prod_proto_rawDescGZIP() []byte {
	file_Prod_proto_rawDescOnce.Do(func() {
		file_Prod_proto_rawDescData = protoimpl.X.CompressGZIP(file_Prod_proto_rawDescData)
	})
	return file_Prod_proto_rawDescData
}
var file_Prod_proto_msgTypes = make([]protoimpl.MessageInfo, 2)
var file_Prod_proto_goTypes = []interface{}{
	(*ProdRequest)(nil),  // 0: services.ProdRequest
	(*ProdResponse)(nil), // 1: services.ProdResponse
}
var file_Prod_proto_depIdxs = []int32{
	0, // 0: services.ProductService.GetProductStock:input_type -> services.ProdRequest
	1, // 1: services.ProductService.GetProductStock:output_type -> services.ProdResponse
	1, // [1:2] is the sub-list for method output_type
	0, // [0:1] is the sub-list for method input_type
	0, // [0:0] is the sub-list for extension type_name
	0, // [0:0] is the sub-list for extension extendee
	0, // [0:0] is the sub-list for field type_name
}
func init() { file_Prod_proto_init() }
func file_Prod_proto_init() {
	if File_Prod_proto != nil {
		return
	}
	if !protoimpl.UnsafeEnabled {
		file_Prod_proto_msgTypes[0].Exporter = func(v interface{}, i int) interface{} {
			switch v := v.(*ProdRequest); i {
			case 0:
				return &v.state
			case 1:
				return &v.sizeCache
			case 2:
				return &v.unknownFields
			default:
				return nil
			}
		}
		file_Prod_proto_msgTypes[1].Exporter = func(v interface{}, i int) interface{} {
			switch v := v.(*ProdResponse); i {
			case 0:
				return &v.state
			case 1:
				return &v.sizeCache
			case 2:
				return &v.unknownFields
			default:
				return nil
			}
		}
	}
	type x struct{}
	out := protoimpl.TypeBuilder{
		File: protoimpl.DescBuilder{
			GoPackagePath: reflect.TypeOf(x{}).PkgPath(),
			RawDescriptor: file_Prod_proto_rawDesc,
			NumEnums:      0,
			NumMessages:   2,
			NumExtensions: 0,
			NumServices:   1,
		},
		GoTypes:           file_Prod_proto_goTypes,
		DependencyIndexes: file_Prod_proto_depIdxs,
		MessageInfos:      file_Prod_proto_msgTypes,
	}.Build()
	File_Prod_proto = out.File
	file_Prod_proto_rawDesc = nil
	file_Prod_proto_goTypes = nil
	file_Prod_proto_depIdxs = nil
}
// Reference imports to suppress errors if they are not otherwise used.
var _ context.Context
var _ grpc.ClientConnInterface
// This is a compile-time assertion to ensure that this generated file
// is compatible with the grpc package it is being compiled against.
const _ = grpc.SupportPackageIsVersion6
// ProductServiceClient is the client API for ProductService service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://godoc.org/google.golang.org/grpc#ClientConn.NewStream.
type ProductServiceClient interface {
	GetProductStock(ctx context.Context, in *ProdRequest, opts ...grpc.CallOption) (*ProdResponse, error)
}
type productServiceClient struct {
	cc grpc.ClientConnInterface
}
func NewProductServiceClient(cc grpc.ClientConnInterface) ProductServiceClient {
	return &productServiceClient{cc}
}
func (c *productServiceClient) GetProductStock(ctx context.Context, in *ProdRequest, opts ...grpc.CallOption) (*ProdResponse, error) {
	out := new(ProdResponse)
	err := c.cc.Invoke(ctx, "/services.ProductService/GetProductStock", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}
// ProductServiceServer is the server API for ProductService service.
type ProductServiceServer interface {
	GetProductStock(context.Context, *ProdRequest) (*ProdResponse, error)
}
// UnimplementedProductServiceServer can be embedded to have forward compatible implementations.
type UnimplementedProductServiceServer struct {
}
func (*UnimplementedProductServiceServer) GetProductStock(context.Context, *ProdRequest) (*ProdResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method GetProductStock not implemented")
}
func RegisterProductServiceServer(s *grpc.Server, srv ProductServiceServer) {
	s.RegisterService(&_ProductService_serviceDesc, srv)
}
func _ProductService_GetProductStock_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(ProdRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(ProductServiceServer).GetProductStock(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/services.ProductService/GetProductStock",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(ProductServiceServer).GetProductStock(ctx, req.(*ProdRequest))
	}
	return interceptor(ctx, in, info, handler)
}
var _ProductService_serviceDesc = grpc.ServiceDesc{
	ServiceName: "services.ProductService",
	HandlerType: (*ProductServiceServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "GetProductStock",
			Handler:    _ProductService_GetProductStock_Handler,
		},
	},
	Streams:  []grpc.StreamDesc{},
	Metadata: "Prod.proto",
}
```
## 创建GRPC服务端
在第一节中，我们依葫芦画瓢做了一个"中间文件"，并生成对应的 **go** 文件，只不过看起来好像没啥用，接下来我们就要创建真正的服务。
## 引入Service
只需要修改 **Prod.proto**文件，添加如下内容 **ProductService**
```bash
syntax="proto3";
package services;
option go_package = "../services";
message ProdRequest {
    int32 prod_id = 1; //商品ID
}
message ProdResponse {
    int32 prod_stock = 1; //商品库存
}
service ProductService {
    rpc  GetProductStock (ProdRequest) returns (ProdResponse);
} 
```
然后生成我们新的 **Prod.proto.go** 文件，同时包含了 **Service** 文件
```bash
protoc --go_out=plugins=grpc:../services Prod.proto
```
## 创建实现类
下面我们就可以创建一个实现类了，在 **services** 文件夹下创建 **ProdService** 文件
![image-20210717090052476](images/image-20210717090052476.png)
文件内容如下，只需要实现我们对应的方法即可
```go
/**
 * @Description
 * @Author 陌溪
 * @Date 2021/7/17 8:56
 **/
package services
import (
	"context"
	"google.golang.org/grpc"
	"log"
)
// 定义的结构体
type ProdService struct {
}
func (this *ProdService) GetProductStock(ctx context.Context, in *ProdRequest, opts ...grpc.CallOption) (*ProdResponse, error) {
	log.Fatalln("进来了")
	return &ProdResponse{ ProdStock: 20}, nil
}
```
## 创建RPC服务
最后，为了使我们的 **RPC** 进行启动，我们还需要对服务进行启动
```GO
package main
import (
	"log"
	"net"
	"github.com/zhuge20100104/grpc-demo/grpc-1/server/services"
	"google.golang.org/grpc"
)
func main() {
	// 通过grpc创建一个Server
	rpcServer := grpc.NewServer()
	// 注册Service
	services.RegisterProductServiceServer(rpcServer, new(services.ProdService))
	// 监听一个端口
	listen, err := net.Listen("tcp", ":8888")
	if err != nil {
		log.Fatalf("启动网络监听失败 %v\n", err)
	}
	log.Print("服务器成功监听8888端口")
	// 进行通信
	rpcServer.Serve(listen)
}
```