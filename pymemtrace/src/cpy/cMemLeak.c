/*
 * Created by Paul Ross on 07/11/2020.
 *
 * Functions to cause memory memory usage and leaks in C and CPython.
 *
*/
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "structmember.h"

/******** Allocate a buffer with C's malloc() ********/
typedef struct {
    PyObject_HEAD
    size_t size;
    void *buffer; /* Buffer created by malloc() */
} CMallocObject;

static void
CMallocObject_dealloc(CMallocObject *self) {
    free(self->buffer);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyObject *
CMallocObject_new(PyTypeObject *type, PyObject *Py_UNUSED(args), PyObject *Py_UNUSED(kwds)) {
    CMallocObject *self;
    self = (CMallocObject *) type->tp_alloc(type, 0);
    if (self != NULL) {
        self->size = 0;
        self->buffer = NULL;
    }
    return (PyObject *) self;
}

static int
CMallocObject_init(CMallocObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = {"size", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "n", kwlist, &self->size)) {
        return -1;
    }
    if (self->size == 0) {
        self->size = 1;
    }
    self->buffer = malloc(self->size);
    if (self->buffer == NULL) {
        return -1;
    }
    return 0;
}

static PyMemberDef CMallocObject_members[] = {
    {"size", T_ULONG, offsetof(CMallocObject, size), 0, "Buffer size."},
    {NULL, 0, 0, 0, NULL}  /* Sentinel */
};

static PyGetSetDef CMallocObject_getsetters[] = {
    {NULL, NULL, NULL, NULL, NULL}  /* Sentinel */
};

static PyMethodDef CMallocObject_methods[] = {
    {NULL, NULL, 0, NULL}  /* Sentinel */
};

PyDoc_STRVAR(
    CMallocObjectType_tp_doc,
    "A simple Python object that reserves a block of C memory with malloc()."
    " Actual reserved memory is always >=1 byte."
);

static PyTypeObject CMallocObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "cMemLeak.CMallocObject",
    .tp_doc = CMallocObjectType_tp_doc,
    .tp_basicsize = sizeof(CMallocObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = CMallocObject_new,
    .tp_init = (initproc) CMallocObject_init,
    .tp_dealloc = (destructor) CMallocObject_dealloc,
    .tp_members = CMallocObject_members,
    .tp_methods = CMallocObject_methods,
    .tp_getset = CMallocObject_getsetters,
};
/******** END: Allocate a buffer with C's malloc() ********/

/******** Allocate a buffer with Python's raw memory interface ********/
typedef struct {
    PyObject_HEAD
    size_t size;
    void *buffer; /* Buffer created by PyMem_RawMalloc() */
} PyRawMallocObject;

static void
PyRawMallocObject_dealloc(PyRawMallocObject *self) {
    PyMem_RawFree(self->buffer);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyObject *
PyRawMallocObject_new(PyTypeObject *type, PyObject *Py_UNUSED(args), PyObject *Py_UNUSED(kwds)) {
    PyRawMallocObject *self;
    self = (PyRawMallocObject *) type->tp_alloc(type, 0);
    if (self != NULL) {
        self->size = 0;
        self->buffer = NULL;
    }
    return (PyObject *) self;
}

static int
PyRawMallocObject_init(PyRawMallocObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = {"size", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "n", kwlist, &self->size)) {
        return -1;
    }
    if (self->size == 0) {
        self->size = 1;
    }
    self->buffer = PyMem_Malloc(self->size);
    if (self->buffer == NULL) {
        return -1;
    }
    return 0;
}

static PyMemberDef PyRawMallocObject_members[] = {
    {"size", T_ULONG, offsetof(PyRawMallocObject, size), 0, "Buffer size."},
    {NULL, 0, 0, 0, NULL}  /* Sentinel */
};

static PyGetSetDef PyRawMallocObject_getsetters[] = {
    {NULL, NULL, NULL, NULL, NULL}  /* Sentinel */
};

static PyMethodDef PyRawMallocObject_methods[] = {
    {NULL, NULL, 0, NULL}  /* Sentinel */
};

PyDoc_STRVAR(
    PyRawMallocObjectType_tp_doc,
    "A simple Python object that reserves a block of memory with Pythons raw memory allocator."
    " Actual reserved memory is always >=1 byte."
);

static PyTypeObject PyRawMallocObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "cMemLeak.PyRawMallocObject",
    .tp_doc = PyRawMallocObjectType_tp_doc,
    .tp_basicsize = sizeof(PyRawMallocObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = PyRawMallocObject_new,
    .tp_init = (initproc) PyRawMallocObject_init,
    .tp_dealloc = (destructor) PyRawMallocObject_dealloc,
    .tp_members = PyRawMallocObject_members,
    .tp_methods = PyRawMallocObject_methods,
    .tp_getset = PyRawMallocObject_getsetters,
};
/******** END: Allocate a buffer with Python's raw memory interface ********/

/******** Allocate a buffer with Python's pymalloc memory interface ********/
typedef struct {
    PyObject_HEAD
    size_t size;
    void *buffer; /* Buffer created by PyMem_Malloc() */
} PyMallocObject;

static void
PyMallocObject_dealloc(PyMallocObject *self) {
    PyMem_Free(self->buffer);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyObject *
PyMallocObject_new(PyTypeObject *type, PyObject *Py_UNUSED(args), PyObject *Py_UNUSED(kwds)) {
    PyMallocObject *self;
    self = (PyMallocObject *) type->tp_alloc(type, 0);
    if (self != NULL) {
        self->size = 0;
        self->buffer = NULL;
    }
    return (PyObject *) self;
}

static int
PyMallocObject_init(PyMallocObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = {"size", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "n", kwlist, &self->size)) {
        return -1;
    }
    if (self->size == 0) {
        self->size = 1;
    }
    self->buffer = PyMem_Malloc(self->size);
    if (self->buffer == NULL) {
        return -1;
    }
    return 0;
}

static PyMemberDef PyMallocObject_members[] = {
    {"size", T_ULONG, offsetof(PyMallocObject, size), 0, "Buffer size."},
    {NULL, 0, 0, 0, NULL}  /* Sentinel */
};

static PyGetSetDef PyMallocObject_getsetters[] = {
    {NULL, NULL, NULL, NULL, NULL}  /* Sentinel */
};

static PyMethodDef PyMallocObject_methods[] = {
    {NULL, NULL, 0, NULL}  /* Sentinel */
};

PyDoc_STRVAR(
    PyMallocObjectType_tp_doc,
    "A simple Python object that reserves a block of memory with Pythons pymalloc allocator."
    " Actual reserved memory is always >=1 byte."
);

static PyTypeObject PyMallocObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "cMemLeak.PyMallocObject",
    .tp_doc = PyMallocObjectType_tp_doc,
    .tp_basicsize = sizeof(PyMallocObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = PyMallocObject_new,
    .tp_init = (initproc) PyMallocObject_init,
    .tp_dealloc = (destructor) PyMallocObject_dealloc,
    .tp_members = PyMallocObject_members,
    .tp_methods = PyMallocObject_methods,
    .tp_getset = PyMallocObject_getsetters,
};
/******** END: Allocate a buffer with Python's pymalloc memory interface ********/

/*
 * Increments the reference count of the supplied PyObject.
 * This will cause a memory leak.
 */
static PyObject *
py_incref(PyObject *Py_UNUSED(module), PyObject *pobj) {
    Py_INCREF(pobj);
    Py_RETURN_NONE;
}

/*
 * Decrements the reference count of the supplied PyObject.
 * This may cause a segfault.
 */
static PyObject *
py_decref(PyObject *Py_UNUSED(module), PyObject *pobj) {
    Py_DECREF(pobj);
    Py_RETURN_NONE;
}

/*
 * Returns a Python bytes object of specified size.
 * The content is uninitialised.
 */
static PyObject *
py_bytes_of_size(PyObject *Py_UNUSED(module), PyObject *args, PyObject *kwds) {
    static char *kwlist[] = {"size", NULL};
    size_t size;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "n", kwlist, &size)) {
        return NULL;
    }
    return PyBytes_FromStringAndSize(NULL, size);
}

static PyMethodDef MemLeakMethods[] = {
    {"py_incref",   (PyCFunction) py_incref, METH_O,
     "Increment the reference count of the Python object."},
    {"py_decref",   (PyCFunction) py_decref, METH_O,
     "Decrement the reference count of the Python object."},
    {"py_bytes_of_size",   (PyCFunction) py_bytes_of_size, METH_VARARGS | METH_KEYWORDS,
     "Returns a Python bytes object of specified size. The content is uninitialised."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static PyModuleDef cMemLeakmodule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "cMemLeak",
    .m_doc = "A module that contains a variety of ways of exercising memory and creating memory leaks on demand.",
    .m_size = -1,
    .m_methods = MemLeakMethods,
};

PyMODINIT_FUNC
PyInit_cMemLeak(void) {
    PyObject *m;
    m = PyModule_Create(&cMemLeakmodule);
    if (m == NULL) {
        return NULL;
    }
    /* C malloc() */
    if (PyType_Ready(&CMallocObjectType) < 0) {
        return NULL;
    }
    Py_INCREF(&CMallocObjectType);
    if (PyModule_AddObject(m, "CMalloc", (PyObject *) &CMallocObjectType) < 0) {
        Py_DECREF(&CMallocObjectType);
        Py_DECREF(m);
        return NULL;
    }
    /* Python raw malloc() */
    if (PyType_Ready(&PyRawMallocObjectType) < 0) {
        return NULL;
    }
    Py_INCREF(&PyRawMallocObjectType);
    if (PyModule_AddObject(m, "PyRawMalloc", (PyObject *) &PyRawMallocObjectType) < 0) {
        Py_DECREF(&PyRawMallocObjectType);
        Py_DECREF(m);
        return NULL;
    }
    /* Python pymalloc() */
    if (PyType_Ready(&PyMallocObjectType) < 0) {
        return NULL;
    }
    Py_INCREF(&PyMallocObjectType);
    if (PyModule_AddObject(m, "PyMalloc", (PyObject *) &PyMallocObjectType) < 0) {
        Py_DECREF(&PyMallocObjectType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}