class Equipments_Tools_Removed {
    constructor(options) {
        "use strict";
        options = options || {};

        const self = this;
        const defaultOptions = {
            data: {
                id: null,
                equipment_id: null,
            },

            table: {
                id: "#table_equipments_tools_removed",

                equipment: {
                    id: null,
                },

                ajax: {
                    url: "/get_equipment_tools_removed/",
                    type: "POST",
                    dataSrc: "data",
                    data: function (d) {
                        return {
                            ...d,
                            equipment_id: self.data.id || null,
                        };
                    },
                },

                order: [[0, "desc"]],

                columns: [
                    {
                        title: "ID",
                        data: "id",
                        className: "text-center toggleable",
                    },
                    {
                        title: "Identificador",
                        data: "identifier",
                        className: "text-center toggleable",

                        render: function (data) {
                            return data || "";
                        },
                    },
                    {
                        title: "Nombre del equipo",
                        data: "equipment_tool__equipment_name",
                        className: "text-center toggleable",
                        render: function (data) {
                            return data || "";
                        },
                    },

                    {
                        title: "Último responsable",
                        data: "last_responsible",
                        className: "text-center toggleable",

                        render: function (data) {
                            return data || "Sin responsable";
                        },
                    },
                    {
                        title: "Estado",
                        data: "state",
                        className: "text-center toggleable",

                        render: function (data) {
                            if (!data) {
                                return "";
                            }

                            switch (data) {
                                case "BAJA":
                                    return `
                                        <span class="badge bg-outline-danger">
                                            Baja
                                        </span>
                                    `;

                                case "DISPONIBLE":
                                    return `
                                        <span class="badge bg-outline-success">
                                            Disponible
                                        </span>
                                    `;

                                case "ASIGNADO":
                                    return `
                                        <span class="badge bg-outline-warning">
                                            Asignado
                                        </span>
                                    `;

                                default:
                                    return `
                                        <span class="badge bg-outline-secondary">
                                            ${data}
                                        </span>
                                    `;
                            }
                        },
                    },
                    {
                        title: "Evidencia 1",
                        data: "evidence1_image",
                        className: "text-center toggleable",
                        orderable: false,

                        render: function (data) {
                            if (!data) {
                                return `
                                    <span class="text-muted">
                                        Sin evidencia
                                    </span>
                                `;
                            }

                            return `
                                <a href="${data}"
                                   target="_blank"
                                   class="btn btn-sm btn-info-light"
                                   title="Ver evidencia 1">
                                    <i class="fa-solid fa-image"></i>
                                    Ver
                                </a>
                            `;
                        },
                    },

                    {
                        title: "Evidencia 2",
                        data: "evidence2_image",
                        className: "text-center toggleable",
                        orderable: false,

                        render: function (data) {
                            if (!data) {
                                return `
                                    <span class="text-muted">
                                        Sin evidencia
                                    </span>
                                `;
                            }

                            return `
                                <a href="${data}"
                                   target="_blank"
                                   class="btn btn-sm btn-info-light"
                                   title="Ver evidencia 2">
                                    <i class="fa-solid fa-image"></i>
                                    Ver
                                </a>
                            `;
                        },
                    },

                    {
                        title: "Motivo de baja",
                        data: "deactivation_reason",
                        className: "text-center toggleable",

                        render: function (data) {
                            if (!data) {
                                return "";
                            }

                            const motivos = {
                                VENDIDO: "Vendido",
                                OBSOLETO: "Obsoleto",
                                PERDIDO: "Perdido",
                                BAJA: "Baja",
                                ROBADO: "Robado",
                            };

                            return motivos[data] || data;
                        },
                    },

                    {
                        title: "Descripción",
                        data: "deactivation_description",
                        className: "text-start toggleable",

                        render: function (data) {
                            if (!data) {
                                return `
                                    <span class="text-muted">
                                        Sin descripción
                                    </span>
                                `;
                            }

                            return data;
                        },
                    },

                    {
                        title: "Fecha de baja",
                        data: "deactivated_at",
                        className: "text-center toggleable",

                        render: function (data, type, row) {
                            // Valor utilizado para ordenar
                            if (type === "sort" || type === "type") {
                                return row.deactivated_at_sort || "";
                            }

                            // Valor mostrado
                            return data || "";
                        },
                    },

                    {
                        title: "Usuario que realizó la baja",
                        data: "user_modification",
                        className: "text-center toggleable",

                        render: function (data) {
                            return data || "";
                        },
                    },
                ],
            },

            userPermissionTable: {},
        };

        self.data = {
            ...defaultOptions.data,
            ...(options.data || {}),
        };

        if (options.table) {
            self.table = {
                ...defaultOptions.table,
                ...options.table,
            };
        } else {
            self.table = defaultOptions.table;
        }

        if (options.userPermissionTable) {
            self.userPermissionTable = {
                ...defaultOptions.userPermissionTable,
                ...options.userPermissionTable,
            };
        }

        self.table.ajax.dataSrc = function (d) {
            if (d.counters) {
                $("#counter-todos").text(d.counters.total || 0);

                $("#counter-activo").text(d.counters.activos || 0);

                $("#counter-inactivos").text(d.counters.inactivos || 0);
            }

            return d.data || [];
        };

        self.init();
    }

    init() {
        const self = this;

        if (self.table) {
            self.tbl_info = $(self.table.id).DataTable({
                processing: true,
                serverSide: false,
                ajax: {
                    url: self.table.ajax.url,
                    type: self.table.ajax.type,
                    dataSrc: self.table.ajax.dataSrc,
                    data: function (d) {
                        return {
                            ...d,
                            equipment_id: self.data.id || null,
                        };
                    },
                },

                columns: self.table.columns,
                responsive: true,
                autoWidth: false,
                order: [[0, "desc"]],

                language: {
                    url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
                },

                dom:
                    "<'row justify-content-between'<'col-md'l><'col-md text-center'B><'col-md'f>>" +
                    "<'row mt-2'<'col-md-12'<'table-responsive pb-1'tr>>>" +
                    "<'row mt-2 justify-content-between'<'col-md-auto me-auto'i><'col-md-auto ms-auto'p>>",

                buttons: [
                    {
                        extend: "colvis",
                        text: "Columnas",
                        columns: function (idx, data, node) {
                            return $(node).hasClass("toggleable");
                        },

                        className: "btn-sm",
                    },
                ],

                pageLength: 10,

                lengthMenu: [
                    [10, 25, 50, 100, -1],
                    [10, 25, 50, 100, "Todos"],
                ],

                initComplete: function (settings, json) {},
            });
        }
    }

    reloadTable() {
        const self = this;
        if (self.tbl_info && $.fn.DataTable.isDataTable(self.table.id)) {
            self.tbl_info.ajax.reload(null, false);
        }
    }

    setEquipmentId(equipmentId) {
        const self = this;

        self.data.id = equipmentId;
        self.data.equipment_id = equipmentId;

        if (self.tbl_info) {
            self.tbl_info.ajax.reload(null, false);
        }
    }

    getEquipmentId() {
        return this.data.id || null;
    }
}

$(document).ready(function () {
    window.equipmentsToolsRemoved = new Equipments_Tools_Removed();
});
