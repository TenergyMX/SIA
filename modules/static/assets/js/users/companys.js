class Company {
    constructor(options) {
        "use strict";

        const self = this;
        const defaultOptions = {
            data: {},
            table: {
                id: "#table_companys",
                ajax: {
                    url: "/get-companys/",
                    dataSrc: "data",
                },
                columns: [
                    { title: "Nombre", data: "name" },
                    { title: "Direccion", data: "address" },
                ],
            },
            list: {
                id: 'select[name"company_id"]',
                ajax: {
                    url: function () {
                        return "/get_users_with_access/";
                    },
                },
            },
        };

        self.data = defaultOptions.data;

        if (options.list) {
            self.list = { ...defaultOptions.list, ...options.list };
            self.list.ajax.reload = function () {
                $.ajax({
                    type: "GET",
                    url: "/get-companys/",
                    data: {
                        isList: true,
                    },
                    beforeSend: function () {},
                    success: function (response) {
                        var select = $(self.list.id);
                        select.html(null);
                        $.each(response["data"], function (index, value) {
                            select.append(
                                `<option value="${value["id"]}">
                                ${value["name"]}
                            </option>`
                            );
                        });
                    },
                    error: function (xhr, status, error) {},
                    complete: function (data) {},
                });
            };
        }

        if (options.table) {
            self.table = { ...defaultOptions.table, ...options.table };
        }

        self.init();
    }

    init() {
        const self = this;

        if (self.list) {
            self.list.ajax.reload();
        }

        if (self.table) {
            self.tbl_companys = $(self.table.id).DataTable({
                ajax: {
                    url: self.table.ajax.url,
                    dataSrc: self.table.ajax.dataSrc,
                    data: self.table.ajax.data,
                },
                columns: self.table.columns,
                order: [
                    [0, "asc"],
                    [1, "asc"],
                ],
                language: {
                    url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
                },
            });
            delete self.table;
        }

        self.setupEventHandlers();
    }

    setupEventHandlers() {
        const self = this;
    }
}
