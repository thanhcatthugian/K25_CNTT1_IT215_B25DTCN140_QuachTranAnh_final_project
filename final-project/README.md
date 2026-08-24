readme_content = """# Hệ Thống Quản Lý Dự Án & Công Việc (Task Management API)

> Một hệ thống Backend API được xây dựng bằng **FastAPI** và **SQLAlchemy**, cung cấp các tính năng quản lý người dùng, phân quyền dự án, quản lý công việc (task), đính kèm tệp tin, bình luận và ghi log thao tác hệ thống tự động.

---

## 📖 Mục Lục
- [Giới Thiệu](#-giới-thiệu)
- [Tính Năng Chính](#-tính-năng-chính)
- [Cấu Trúc Cơ Sở Dữ Liệu](#-cấu-trúc-cơ-sở-dữ-liệu)
- [Công Nghệ Sử Dụng](#-công-nghệ-sử-dụng)
- [Cài Đặt & Chạy Dự Án](#-cài-đặt--chạy-dự-án)
- [Tài Liệu API Endpoints](#-tài-liệu-api-endpoints)
- [Hệ Thống Logging](#-hệ-thống-logging)

---

## 🚀 Giới Thiệu
Dự án này là một API RESTful toàn diện hỗ trợ làm việc nhóm, cho phép người dùng tạo và quản lý dự án, phân công nhiệm vụ (task), theo dõi tiến độ công việc, tải lên tài liệu đính kèm và trao đổi thông tin qua hệ thống bình luận. Hệ thống tích hợp bảo mật JWT và phân quyền chi tiết cho từng thành viên trong dự án.

---

## ✨ Tính Năng Chính
- **Xác thực & Phân quyền:** Đăng ký, đăng nhập bảo mật bằng mật khẩu mã hóa `bcrypt` và xác thực `JWT Token`. Phân quyền linh hoạt (`admin` / `user`).
- **Quản lý Dự án (Projects):** Tạo, xem danh sách, tìm kiếm, cập nhật và xóa mềm (soft delete) dự án.
- **Quản lý Thành viên (Project Members):** Thêm thành viên vào dự án, phân vai trò (`owner`, `member`), cơ chế "hồi sinh" thành viên đã bị xóa, và quản lý danh sách thành viên.
- **Quản lý Công việc (Tasks):** Tạo task, cập nhật trạng thái (`todo`, `in_progress`, `done`), độ ưu tiên (`low`, `medium`, `high`), hạn hoàn thành (`due_date`), tìm kiếm task thông minh, phân trang theo thời gian tạo.
- **Tệp đính kèm & Bình luận:** Hỗ trợ tải lên file (`jpg`, `png`, `pdf`, `docx`) vào task và thêm bình luận thảo luận.
- **Ghi nhật ký (Logging):** Tự động ghi lại lịch sử thao tác hệ thống và các lỗi phát sinh vào file `app.log`.

---

## 🏛️ Cấu Trúc Cơ Sở Dữ Liệu
Hệ thống sử dụng cơ sở dữ liệu quan hệ gồm 5 bảng chính:
1. **Users:** Quản lý thông tin tài khoản, mật khẩu băm, vai trò và trạng thái hoạt động.
2. **Projects:** Lưu thông tin dự án, chủ sở hữu (`owner_id`) và cờ xóa mềm.
3. **ProjectMembers:** Bảng trung gian quản lý quan hệ nhiều-nhiều giữa User và Project kèm vai trò cụ thể.
4. **Tasks:** Lưu trữ công việc thuộc về dự án, người thực hiện (`assignee_id`), trạng thái và file đính kèm.
5. **Comments:** Lưu bình luận trao đổi gắn liền với từng task.

---

## 💻 Công Nghệ Sử Dụng
- **Python 3.9+**
- **FastAPI** (Framework xây dựng API hiệu năng cao)
- **SQLAlchemy** (ORM tương tác cơ sở dữ liệu)
- **Pydantic / Pydantic Settings** (Xác thực dữ liệu và quản lý cấu hình)
- **PyJWT & Bcrypt** (Bảo mật và mã hóa)
- **Uvicorn** (ASGI Server)

---

## ⚙️ Cài Đặt & Chạy Dự Án

1. **Clone repository và di chuyển vào thư mục dự án:**
   ```bash
   git clone <repository-url>
   cd <project-folder>


⠀⠀⠀⠀⠤⣬⣭⣕⣒⡒⠤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠐⠲⠬⣍⡛⠿⣷⣮⡑⢦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠈⠉⠓⠶⣄⡙⢷⡈⢻⣿⣦⠱⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠸⣷⠈⣿⠀⣿⣿⣧⢡⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣀⣤⡟⢰⣿⠀⣿⣿⣿⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣠⣴⣾⡿⠟⢁⣴⣿⢏⣼⣿⣿⢏⡼⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢀⣴⣿⡟⠉⢀⣴⣿⠟⣵⣿⣿⡟⣣⡾⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣼⣿⡟⠀⠀⣼⣿⠇⣿⣿⣿⠟⡸⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢿⣿⡇⠀⠸⣿⣏⠀⣿⣿⣏⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠈⠻⣿⣄⡀⠙⢿⣦⣘⠿⣿⣆⠈⠦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠈⠛⠿⣶⣤⣈⠛⠷⣌⡛⠷⣦⡈⠓⠦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠈⠉⠙⠳⠶⣤⡙⠳⢤⣉⠳⢦⣀⠉⠒⢄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠓⣦⡙⣷⣄⠉⠻⣦⡀⠑⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⡷⢸⣿⣷⡀⠘⢿⣆⠈⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣀⣄⣠⣤⣤⠶⠞⢋⣥⣾⣿⡿⠁⠀⣸⣿⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣴⣿⡿⠛⢉⣠⣴⣶⣿⠿⠟⠛⢉⣀⣤⣶⡿⠃⡰⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣼⣿⠋⢀⣴⣿⡿⠟⠉⣀⣤⣶⡿⢟⣫⠭⠅⠒⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣿⠇⠀⣾⣿⡿⠁⠀⣼⣿⣿⠋⣴⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⡀
⠀⠀⠠⣿⠀⠀⣿⣿⡇⠀⠀⠹⣿⣿⣄⠹⢿⣤⣤⡤⠤⢤⣤⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣶⣿⣿⣿⣿⣿
⠀⠀⠀⢻⣆⠀⠸⣿⣿⣄⡀⠀⠈⠛⠛⠛⠓⠒⠲⠶⢶⣦⡌⢻⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⠟⠛⠛⠻⢿⣿
⠀⠀⠀⠈⠻⣦⣄⡈⠛⠿⠿⣷⣶⠶⠶⠶⠶⠿⣿⣶⡄⢻⡇⢀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡟⢁⣴⣿⣿⣆⠀⠈
⠀⠀⠀⠀⠀⠀⠉⠛⠛⣶⣶⣶⣶⣶⣾⣿⣿⣶⡌⣿⣿⢸⡇⢰⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡏⢰⣿⣿⣿⣿⣿⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠙⠻⣿⣿⣷⢸⣿⠸⡇⢸⠀⠀⠀⠀⠀⠀⠀⠀⣰⢏⣴⣿⠿⢿⣿⣿⡏⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⡄⣿⡄⣇⢸⣄⠀⠀⠀⠀⢀⣠⠞⣥⡾⠋⠀⠀⠀⢹⣿⠁⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⡇⢿⣧⢻⣄⠙⠿⠶⠶⢛⣫⣵⡾⠋⠀⣠⣴⣤⠀⢸⡟⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣷⡘⣿⣧⡈⠛⠲⠶⠿⠟⠛⠉⢀⣴⣾⠿⢿⣿⡇⢸⣷⡀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣌⠛⠿⣷⣤⣤⣤⣤⣴⠾⣻⣭⣶⣶⣦⣌⢿⣄⠙⠿⠿⠿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠿⣦⣤⣈⣉⣡⡤⠶⠛⠉⠀⠀⠀⠈⠙⢷⣝⠳⢦⣄⣀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠳⢦⣍⣉